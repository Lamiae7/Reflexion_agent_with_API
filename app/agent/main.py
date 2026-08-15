from app.agent.graph import build_graph
import sys





DEFAULT_QUESTION = (
    "Quelle est la position concurrentielle de Mistral AI face à OpenAI et Anthropic en 2026 ?"
)

def main() -> None :
    question = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_QUESTION
    
    print(f"Question du user {question}\n")
    
    print("Compilation du graphe")
    
    app = build_graph()
    
    messages = app.invoke(question)
    
    step = 0
    
    for msg in messages :
        
        tool_calls = getattr(msg, "tool_calls", None) # pour éviter de tomber dans une erreur, on met None par default.
        
        if not tool_calls :
            
            continue
        
        for call in tool_calls:
            
            args = call.get("args", {}) # call étant un disctionnaire, donc on fait le get.
            
            if "answer" not in args:
                
                continue # car on sait jamais si le llm va produire la sortie avec le shéma souhaité.
            
            step += 1
            
            print(f"{'='*60}")
            
            print(f"Etape {step} ({call['name']})")
            
            print(f"{'=' * 60}")
            
            reflection = args.get("reflection", {})
            
            if reflection :
                
                print(f"Manque{reflection.get('missing', 'rien :)')}")
                
                print(f"Superflu{reflection.get('superluous', 'rien :)')}")
                
            if args.get("search_queries") :
                
                print(f"Requette de recherche générés : {args['search_queries']}")
                
                
            if args.get("references"):
                print("Références :")
                for ref in args["references"]:
                    print(f"  {ref}")
                print()
                
                
            print(f"{'-' * 60}")
            
            
if __name__ == "__main__" :
    main()

            
            
            
    
    
    