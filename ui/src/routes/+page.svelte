<script>
	import 'carbon-components-svelte/css/g100.css';
	import Settings from "carbon-icons-svelte/lib/Settings.svelte";
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
		Switch,
		Modal,
		Button,
		ImageLoader,
		NumberInput, Tag,
		RadioButtonGroup, RadioButton
	} from 'carbon-components-svelte';

	let query = '';
	let loading = false;
	let currentPage = 1;
	let pageSize = 4;
	let results = [];

	let open = false;

	const searchTypes = ['Author', 'Paper'];
	let selectedIndex = 0;
	$: searchType = searchTypes[selectedIndex];


	const models = ["BGE-M3", "all-MiniLM-L6-v2", "IndoBERT (Fine-tuned)"];
	const modelMap = {
		"BGE-M3": "bgem3",
		"all-MiniLM-L6-v2": "allminilm",
		"IndoBERT (Fine-tuned)": "indobert"
	};
	let model = models[0];

	let topK = 100;

	let prevModel;
	let prevTopK;
	let prevSelectedIndex;
	let showResults = false;

	$: if (model !== prevModel || topK !== prevTopK || selectedIndex !== prevSelectedIndex) {
		showResults = false
		query = "";
		prevModel = model;
		prevTopK = topK;
		prevSelectedIndex = selectedIndex;
	}

	async function fetchResults(query) {
		if (!query.trim()) return;

		loading = true;
		try {
			const searchTypeLower = searchType.toLowerCase();
			const normalizedModel = modelMap[model]
			const url = new URL(`http://127.0.0.1:5000/search/${searchTypeLower}/${encodeURIComponent(query)}`);
			url.searchParams.append('topK', String(topK));
			url.searchParams.append('model', normalizedModel);

			const res = await fetch(url.toString());
			if (!res.ok) throw new Error('Failed to fetch data');


			const json = await res.json();
			console.log(json)
			if (searchType === "Paper") {
				results = json.data.topPapers || [];
			} else {
				results = json.data.topAuthors || [];
			}
			console.log(results)
		} catch (e) {
			console.error(e);
			results = [];
		}
		loading = false;
		showResults = true;
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
						on:keydown={(e) => { if (e.key === 'Enter') fetchResults(query) }}
					/>

					<Button kind="tertiary" icon={Settings} iconDescription="Settings" on:click={() => (open = true)}/>
				</div>
				<Tag type="outline">Search Type: {searchType}</Tag>
				<Tag type="outline">Model: {model}</Tag>
				<Tag type="outline">TopK: {topK}</Tag>
        <Loading bind:active={loading}/>

        {#if showResults && !loading}
          <h4 style="padding-top: 2.5rem; padding-bottom: 0.5rem;">Showing results for "{query}"</h4>
          {#each paginatedResults as result, i (i)}
            <ExpandableTile>
              <div slot="above" style="margin-bottom: 1rem">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                  {#if searchType === 'Author'}
                    <div style="display: flex; align-items: center; gap: 1rem;">
                      <div style="width: 60px;">
                        <ImageLoader
                          src="{result.url_picture}"
                          alt="{result.name}"
                          ratio="1x1"
                          style="border-radius: 50%;"
                        />
                      </div>

                      <div>
                        <h4 style="margin: 0;">{result.name}</h4>
                        <h6 style="margin: 0;">Score: {result.combined_score}</h6>
                      </div>
                    </div>
	                  <div style="text-align: right;">
		                  <h6 style="margin: 0;">{result.publication_count} related papers</h6>
	                  </div>
                  {:else}
                    <div>
                      <h4 style="margin: 0;">{result.title}</h4>
                      <h6 style="margin: 0;">Distance: {result.distance}</h6>
                    </div>
	                  <div style="text-align: right;">
		                  <h6 style="margin: 0;">{result.authors}</h6>
	                  </div>
                  {/if}
                </div>
              </div>
              <div slot="below">
	              {#if searchType === 'Author'}
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
	              {:else}
		              {result.abstract}
	              {/if}

              </div>
            </ExpandableTile>
          {/each}
          <Pagination
            totalItems={results.length}
            bind:page={currentPage}
            bind:pageSize={pageSize}
            pageSizes={[4, 10, 20, 50]}
            on:change={handlePaginationChange}
          />
        {/if}
			</Column>   
		</Row>
	</Grid>
</Content>
<Modal
	bind:open size="sm" modalHeading="Settings" hasScrollingContent passiveModal preventCloseOnClickOutside
>
	<Row style="margin-bottom: 2rem;"/>
  <ContentSwitcher bind:selectedIndex style="margin-bottom: 1rem;">
    <Switch text="Author" />
    <Switch text="Paper" />
  </ContentSwitcher>

	<RadioButtonGroup
		legendText="Embedding Model"
		bind:selected={model}
	>
		{#each models as value (value)}
			<RadioButton labelText={value} {value} />
		{/each}
	</RadioButtonGroup>

	<Row style="margin-bottom: 1rem;"/>

	<NumberInput label="Top K" bind:value={topK} helperText="Number of most relevant results to return"/>
</Modal>
