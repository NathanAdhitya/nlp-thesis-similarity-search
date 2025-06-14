<script>
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
		Tile,
		PaginationNav,
		ContentSwitcher,
		Switch,
		ComboBox,
		Modal,
		Button,
		TextInput
	} from 'carbon-components-svelte';

	let query = '';
	let loading = false;
	let currentPage = 1;
	let pageSize = 3;
	let results = [];
	let selectedIndex = 0;
	let showSettings = false;
	let topK = 100;
	

	async function fetchResults(query) {
		if (!query.trim()) return;

		loading = true;
		try {
			const res = await fetch(
				`http://127.0.0.1:5000/search/${mode}/${encodeURIComponent(query)}`
			);
			if (!res.ok) throw new Error('Failed to fetch data');

			const json = await res.json();
			results = json.data.topPapers;
			currentPage = 1;
		} catch (e) {
			console.error(e);
			results = [];
		}
		loading = false;
	}

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
				<h1>Semantica</h1>
				<h6 style="padding-bottom: 1rem;">Semantic Search for Academic Papers</h6>

				<div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
					<Search
						placeholder="Search..."
						size="xl"
						bind:value={query}
						on:input={() => fetchResults(query)}
					/>

					<Button kind="tertiary" size="xl" on:click={() => (showSettings = true)}>
						Settings
					</Button>
				</div>

				<Modal
					open={showSettings}
					on:close={() => (showSettings = false)}
					modalLabel="Search Settings"
					modalHeading="Configure Search Options"
					primaryButtonText="Close"
				>
					<p style="margin-bottom: 1rem;">Search Mode:</p>
					<ContentSwitcher bind:selectedIndex style="margin-bottom: 1rem;">
						<Switch text="Author" />
						<Switch text="Paper" />
					</ContentSwitcher>

					<p style="margin-bottom: 0.5rem;">Model:</p>
					<ComboBox
						titleText="Embedding Model"
						placeholder="Select model"
						items={[
							{ id: '0', text: 'bgem3' },
							{ id: '1', text: 'allminilm' },
							{ id: '2', text: 'indobert' }
						]}
					/>

					<p style="margin-top: 1rem;">Top K Results:</p>
					<TextInput
						type="number"
						bind:value={topK}
						labelText="Top K Results"
						min="1"
						max="1000"
					/>
				</Modal>

				<Loading bind:active={loading} />

				{#if query.trim() !== '' && !loading}
					<h4 style="padding-top: 2.5rem; padding-bottom: 0.5rem;">
						Showing top {topK} results / Showing results with > 0.5 Similarity  0.5 for "{query}" ({mode})
					</h4>

					{#each paginatedResults as result, i (result.id || i)}
						<ExpandableTile>
							<div slot="above" style="margin-bottom: 1rem;">
								<div style="display: flex; justify-content: space-between; align-items: center;">
									<h4 style="margin: 0;">{result.title}</h4>
									<h6 style="margin: 0;">{result.author}</h6>
								</div>
								<h6>Similarity: {result.similarity_score}</h6>
							</div>
							<div slot="below">
								{result.abstract}
							</div>
						</ExpandableTile>
					{/each}

					<Pagination
						totalItems={results.length}
						bind:page={currentPage}
						bind:pageSize
						pageSizes={[3, 5, 10, 20, 50]}
						on:change={handlePaginationChange}
					/>
				{/if}
			</Column>
		</Row>
	</Grid>
</Content>
