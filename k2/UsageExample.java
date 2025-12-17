import java.util.List;
import java.util.concurrent.CompletableFuture;

/**
 * Example usage of SemanticKeywordFinder with String input
 */
public class UsageExample {
    
    public static void main(String[] args) {
        SemanticKeywordFinder finder = new SemanticKeywordFinder();
        
        // Example 1: Basic usage with default parameters (top 3 keywords)
        String content = "This delicious recipe features grilled chicken with fresh herbs " +
                "and organic vegetables. Start by marinating the poultry in olive oil " +
                "and spices for best results. Perfect for those following a low carb " +
                "or paleo diet. You can also try roasting or baking for different flavors.";
        
        CompletableFuture<List<String>> resultFuture = finder.processContentAsync(content);
        
        // Handle the result when it's ready
        resultFuture.thenAccept(keywords -> {
            System.out.println("Top matching keywords:");
            keywords.forEach(keyword -> System.out.println("  - " + keyword));
        }).join(); // Wait for completion
        
        System.out.println();
        
        // Example 2: Custom parameters (top 5 keywords, analyze 2 sentences per keyword)
        CompletableFuture<List<String>> customResultFuture = 
                finder.processContentAsync(content, 5, 2);
        
        customResultFuture.thenAccept(keywords -> {
            System.out.println("Top 5 matching keywords:");
            for (int i = 0; i < keywords.size(); i++) {
                System.out.println((i + 1) + ". " + keywords.get(i));
            }
        }).join();
        
        System.out.println();
        
        // Example 3: Error handling
        String emptyContent = "";
        finder.processContentAsync(emptyContent)
            .thenAccept(keywords -> {
                System.out.println("Success: " + keywords);
            })
            .exceptionally(error -> {
                System.err.println("Error processing content: " + error.getMessage());
                return null;
            })
            .join();
        
        System.out.println();
        
        // Example 4: Chaining operations
        String recipeContent = "Vegan cauliflower steaks with tahini sauce. " +
                "Steam the cauliflower until tender, then glaze with a plant-based " +
                "marinade. Rich in fiber and nutrients, perfect for clean eating.";
        
        finder.processContentAsync(recipeContent, 4, 1)
            .thenApply(keywords -> {
                // Transform the results
                System.out.println("Processing " + keywords.size() + " keywords...");
                return keywords.stream()
                    .map(String::toUpperCase)
                    .toList();
            })
            .thenAccept(uppercaseKeywords -> {
                System.out.println("Keywords in uppercase:");
                uppercaseKeywords.forEach(System.out::println);
            })
            .join();
        
        System.out.println();
        
        // Example 5: Processing multiple documents concurrently
        String doc1 = "Healthy smoothie with berries, nuts, and dairy-free milk.";
        String doc2 = "Grilled seafood with citrus and fresh herbs.";
        String doc3 = "Comfort food: slow cooking beef stew with root vegetables.";
        
        CompletableFuture<List<String>> future1 = finder.processContentAsync(doc1);
        CompletableFuture<List<String>> future2 = finder.processContentAsync(doc2);
        CompletableFuture<List<String>> future3 = finder.processContentAsync(doc3);
        
        // Wait for all to complete
        CompletableFuture.allOf(future1, future2, future3).thenRun(() -> {
            try {
                System.out.println("Document 1 keywords: " + future1.get());
                System.out.println("Document 2 keywords: " + future2.get());
                System.out.println("Document 3 keywords: " + future3.get());
            } catch (Exception e) {
                e.printStackTrace();
            }
        }).join();
    }
}
