# Utility function for displaying search results with customizable options

def print_formatted_results(results, show_authors=True, show_contributors=True, show_abstract=True, show_metrics=True):
    """
    Print formatted search results with customizable display options
    
    Args:
        results: List of search results from ThesisSimilaritySearch.search()
        show_authors: Whether to display author information
        show_contributors: Whether to display contributor information
        show_abstract: Whether to display the abstract
        show_metrics: Whether to display similarity score and distance
    """
    if not results:
        print("No results found.")
        return
        
    for i, result in enumerate(results):
        print(f"\nResult {i+1}: {result['title']}")
        
        # Display metrics if requested
        if show_metrics:
            print(f"  Similarity: {result['similarity_score']:.4f}")
            print(f"  Distance: {result['distance']:.4f}")
        
        # Display authors if requested
        if show_authors and 'authors' in result:
            if result['authors']:
                authors_str = ", ".join(result['authors'])
                print(f"  Authors: {authors_str}")
            else:
                print(f"  Authors: No author information available")
        
        # Display contributors if requested
        if show_contributors and 'contributors' in result:
            if result['contributors']:
                # Group contributors by role
                contributors_by_role = {}
                for contributor in result['contributors']:
                    role = contributor['role']
                    if role not in contributors_by_role:
                        contributors_by_role[role] = []
                    contributors_by_role[role].append(contributor['name'])
                
                # Print contributors by role
                print(f"  Contributors:")
                for role, names in sorted(contributors_by_role.items()):
                    contributors_str = ", ".join(names)
                    print(f"    {role}: {contributors_str}")
            else:
                print(f"  Contributors: No contributor information available")
        
        # Display abstract if requested
        if show_abstract and 'abstract' in result:
            if result['abstract']:
                # Truncate very long abstracts for display
                abstract = result['abstract']
                if len(abstract) > 300:
                    abstract = abstract[:297] + '...'
                print(f"  Abstract: {abstract}")
            else:
                print(f"  Abstract: No abstract available")
