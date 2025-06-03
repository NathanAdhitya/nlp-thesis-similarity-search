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
		PaginationNav
	} from 'carbon-components-svelte';

	let query = '';
	let results = [
		{
			title: "Paper Title A",
			similarity_score: "0.58",
			author: "Author A",
			abstract: "This is abstract. This is abstract. This is abstract. This is abstract. This is abstract. " +
				"This is abstract. This is abstract. This is abstract. This is abstract. This is abstract. " +
				"This is abstract. This is abstract. This is abstract. This is abstract. This is abstract."
		},
		{
			title: "Paper Title B",
			similarity_score: "0.53",
			author: "Author B ",
			abstract: "This is abstract. This is abstract. This is abstract. This is abstract. This is abstract. " +
				"This is abstract. This is abstract. This is abstract. This is abstract. This is abstract. " +
				"This is abstract. This is abstract. This is abstract. This is abstract. This is abstract."
		},
		{
			title: "Paper Title A",
			similarity_score: "0.58",
			author: "Author A",
			abstract: "This is abstract. This is abstract. This is abstract. This is abstract. This is abstract. " +
				"This is abstract. This is abstract. This is abstract. This is abstract. This is abstract. " +
				"This is abstract. This is abstract. This is abstract. This is abstract. This is abstract."
		},
		{
			title: "Paper Title A",
			similarity_score: "0.58",
			author: "Author A",
			abstract: "This is abstract. This is abstract. This is abstract. This is abstract. This is abstract. " +
				"This is abstract. This is abstract. This is abstract. This is abstract. This is abstract. " +
				"This is abstract. This is abstract. This is abstract. This is abstract. This is abstract."
		},
		{
			title: "Paper Title A",
			similarity_score: "0.58",
			author: "Author A",
			abstract: "This is abstract. This is abstract. This is abstract. This is abstract. This is abstract. " +
				"This is abstract. This is abstract. This is abstract. This is abstract. This is abstract. " +
				"This is abstract. This is abstract. This is abstract. This is abstract. This is abstract."
		},
		{
			title: "Paper Title A",
			similarity_score: "0.58",
			author: "Author A",
			abstract: "This is abstract. This is abstract. This is abstract. This is abstract. This is abstract. " +
				"This is abstract. This is abstract. This is abstract. This is abstract. This is abstract. " +
				"This is abstract. This is abstract. This is abstract. This is abstract. This is abstract."
		},

	];

	let loading = false;
	async function fetchResults(text) {
		loading = true
		await new Promise(resolve => setTimeout(resolve, 1500));
		loading = false
	}

	let currentPage = 1;
	let pageSize = 3;

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
				<Search
					placeholder="Search..."
					size="xl"
					bind:value={query}
					on:input={() => fetchResults(query)}
				/>
				<Loading bind:active={loading}/>

				{#if query.trim() !== '' && !loading}
					<h4 style="padding-top: 2.5rem;">Showing top 100 results / Showing results with > 0.5 similarity for "{query}"</h4>
					<Row style="padding-top: 0.5rem; padding-bottom: 1rem;">
						<Column>
							<Tile>
								<h4 style="margin: 0;">Author</h4>
								<h6 style="margin: 0;">Test</h6>
							</Tile>
						</Column>
						<Column>
							<Tile>
								<h4 style="margin: 0;">Author</h4>
								<h6 style="margin: 0;">Test</h6>
							</Tile>
						</Column>
						<Column>
							<Tile>
								<h4 style="margin: 0;">Author</h4>
								<h6 style="margin: 0;">Test</h6>
							</Tile>
						</Column>
						<Column>
							<Tile>
								<h4 style="margin: 0;">Author</h4>
								<h6 style="margin: 0;">Test</h6>
							</Tile>
						</Column>
						<Column>
							<Tile>
								<h4 style="margin: 0;">Author</h4>
								<h6 style="margin: 0;">Test</h6>
							</Tile>
						</Column>
					</Row>
					<Row>
						<PaginationNav style="margin: auto; margin-bottom: 1rem;" total={100} shown={5} />
					</Row>

					{#each paginatedResults as result, i (i)}
						<ExpandableTile>
							<div slot="above" style="margin-bottom: 1rem">
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
						bind:pageSize={pageSize}
						pageSizes={[3, 5, 10, 20, 50]}
						on:change={handlePaginationChange}
					/>
				{/if}
			</Column>
		</Row>
	</Grid>
</Content>
