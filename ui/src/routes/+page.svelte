<script lang="ts">
	import 'carbon-components-svelte/css/g100.css';
	import {
		Search,
		Content,
		Grid,
		Row,
		Column,
		ExpandableTile,
		Pagination,
		Loading,
		ContentSwitcher,
		Switch
	} from 'carbon-components-svelte';

	let query = '';
	let paper = true;
	let selectedIndex = 0;
	$: paper = selectedIndex === 1;

	let results = [];

	let loading = false;
	async function fetchResults(query) {
		if (!query || query.trim() === "") {
			loading = false;
			return;
		}
		loading = true
		const searchType = paper ? "paper" : "author";
		const res = await fetch(`http://127.0.0.1:5000/search/${searchType}/${encodeURIComponent(query)}`);

		if (!res.ok) {
			throw new Error("Failed to fetch data");
		}
		const json = await res.json();
		console.log("API Response:", json.data);
		if (searchType === "paper") {
			results = json.data.topPapers || [];
		} else {
			const authorResults = json.data.topAuthors || [];
			console.log("Author results before processing:", authorResults);
			console.log("Sample author image URL:", authorResults[0]?.url_picture);
			results = authorResults;
		}

		loading = false
	}

	let currentPage = 1;
	let pageSize = 5;

	$: paginatedResults = results.slice((currentPage - 1) * pageSize, currentPage * pageSize);

	function handlePaginationChange(e) {
		const { page, pageSize: newSize } = e.detail;
		currentPage = page;
		pageSize = newSize;
	}
</script>

<Content>
	<Grid>
		<Row>
			<Column>
				<h1 class="">Semantica</h1>
				<h6 style="padding-bottom: 1rem;">Semantic Search for Academic Papers</h6>
				<ContentSwitcher bind:selectedIndex style="margin-bottom: 1rem;">
					<Switch text="Author" />
					<Switch text="Paper" />
				</ContentSwitcher>
				<Search
					placeholder="Search..."
					size="xl"
					bind:value={query}
					on:input={() => fetchResults(query)}
				/>
				<Loading bind:active={loading}/>

				{#if query.trim() !== '' && !loading}
					<h4 style="padding-top: 2.5rem; padding-bottom: 0.5rem;">Showing results for "{query}"</h4>					
					{#each paginatedResults as result, i (i)}
						<ExpandableTile>
							<div slot="above" style="margin-bottom: 1rem">
								<div style="display: flex; justify-content: space-between; align-items: center;">
									{#if !paper}
										<div style="display: flex; align-items: center; gap: 1rem;">
											<img 
												src="{result.url_picture}"
												alt="{result.name}"
												style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover;"
											/>
											<h4 style="margin: 0;">{result.name}</h4>
										</div>
									{:else}
										<h4 style="margin: 0;">{result.name}</h4>
									{/if}
									<h6 style="margin: 0;">{result.publication_count} related papers</h6>
								</div>
								<h6>Score: {result.combined_score}</h6>
							</div>
							<div slot="below">

								{#if result.publications && result.publications.length > 0}
									<ul>
										{#each result.publications as paper, i (i)}
											<li>
												{paper.title || paper.name || "Untitled paper"}
											</li>
										{/each}
									</ul>
								{:else}
									<p>No publications available.</p>
								{/if}
							</div>
						</ExpandableTile>
					{/each}
					<Pagination
						totalItems={results.length}
						bind:page={currentPage}
						bind:pageSize={pageSize}
						pageSizes={[5, 10, 20, 50]}
						on:change={handlePaginationChange}
					/>
				{/if}
			</Column>
		</Row>
	</Grid>
</Content>
