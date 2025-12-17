import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;

public class SemanticKeywordFinder {

    // Verification keywords (same as Python version)
    private static final List<String> VERIFICATION_KEYWORDS = Arrays.asList(
            "Keto", "Paleo", "Vegan", "Vegetarian", "Mediterranean Diet", "Whole30", "Pescatarian", "Flexitarian",
            "Low Carb", "High Protein", "Atkins", "Intermittent Fasting", "Carnivore Diet", "Plant Based", "DASH Diet",
            "Gluten Free", "Dairy Free", "Sugar Free", "Raw Food", "Low FODMAP", "Macrobiotic", "Calorie Counting",
            "Nutrient Dense", "Clean Eating", "Anti Inflammatory", "Baking", "Roasting", "Frying", "Sautéing",
            "Grilling", "Steaming", "Boiling", "Poaching", "Braising", "Stewing", "Broiling", "Barbecue", "Smoking",
            "Sous Vide", "Air Frying", "Slow Cooking", "Pressure Cooking", "Fermenting", "Pickling", "Canning",
            "Blanching", "Caramelizing", "Glazing", "Marinating", "Deep Frying", "Pan Searing", "Wok Cooking",
            "Knife Skills", "Mise en Place", "Meal Prep", "Organic", "Non GMO", "Whole Foods", "Processed Foods",
            "Superfoods", "Comfort Food", "Street Food", "Fine Dining", "Farm to Table", "Sustainable",
            "Locally Sourced", "Seasonal", "Seafood", "Poultry", "Red Meat", "Grains", "Legumes", "Root Vegetables",
            "Leafy Greens", "Cruciferous Vegetables", "Citrus", "Berries", "Stone Fruit", "Nuts", "Seeds", "Dairy",
            "Artisan Cheese", "Spices", "Fresh Herbs", "Sauces", "Condiments", "Healthy Fats", "Probiotics", "Fiber");

    private final EmbeddingEngine embeddingEngine;
    private volatile boolean isProcessing = false;

    public SemanticKeywordFinder() {
        this.embeddingEngine = new TfIdfEmbeddingEngine();
    }

    /**
     * Process a string content and return a CompletableFuture with the top matching keywords
     * 
     * @param content The complete file content as a string
     * @param numResults Number of top keywords to return (default: 3)
     * @param numTopSentences Number of top sentences per keyword (default: 1)
     * @return CompletableFuture containing a list of matching keyword strings
     */
    public CompletableFuture<List<String>> processContentAsync(String content, int numResults, int numTopSentences) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                SearchResults results = processContent(content, numResults, numTopSentences);
                return results.topKeywords.stream()
                        .map(match -> match.keyword)
                        .collect(Collectors.toList());
            } catch (Exception e) {
                throw new CompletionException(e);
            }
        });
    }

    /**
     * Convenience method with default parameters
     * 
     * @param content The complete file content as a string
     * @return CompletableFuture containing a list of the top 3 matching keyword strings
     */
    public CompletableFuture<List<String>> processContentAsync(String content) {
        return processContentAsync(content, 3, 1);
    }

    /**
     * Process content string and find semantic keyword matches
     */
    private SearchResults processContent(String content, int numResults, int numTopSentences) {
        if (content == null || content.isBlank()) {
            throw new IllegalArgumentException("Content is empty or null.");
        }

        // Process document
        List<String> sentences = splitIntoSentences(content);

        if (sentences.isEmpty()) {
            throw new IllegalArgumentException("Could not split the content into sentences.");
        }

        // Build vocabulary and compute embeddings
        embeddingEngine.buildVocabulary(sentences, VERIFICATION_KEYWORDS);

        List<double[]> sentenceEmbeddings = sentences.stream()
                .map(embeddingEngine::embed)
                .collect(Collectors.toList());

        List<double[]> keywordEmbeddings = VERIFICATION_KEYWORDS.stream()
                .map(embeddingEngine::embed)
                .collect(Collectors.toList());

        // Find semantic matches
        return findSemanticMatches(
                sentences, sentenceEmbeddings,
                VERIFICATION_KEYWORDS, keywordEmbeddings,
                numResults, numTopSentences);
    }

    /**
     * Main entry point
     */
    public static void main(String[] args) {
        // Check for help flag first
        for (String arg : args) {
            if (arg.equals("-h") || arg.equals("--help")) {
                printUsage();
                System.exit(0);
            }
        }

        if (args.length < 1) {
            printUsage();
            System.exit(1);
        }

        String filePath = args[0];
        int numResults = 3;
        int numTopSentences = 1;

        // Parse optional arguments
        for (int i = 1; i < args.length; i++) {
            if (args[i].equals("-n") && i + 1 < args.length) {
                numResults = Integer.parseInt(args[++i]);
            } else if (args[i].equals("-s") && i + 1 < args.length) {
                numTopSentences = Integer.parseInt(args[++i]);
            }
        }

        SemanticKeywordFinder finder = new SemanticKeywordFinder();
        finder.processFileAsync(filePath, numResults, numTopSentences);
    }

    private static void printUsage() {
        System.out.println("Semantic Keyword Finder");
        System.out.println("=======================");
        System.out.println("Finds semantic matches between predefined keywords and document content.\n");
        System.out.println("Usage: java -jar semantic-keyword-finder.jar <file> [options]\n");
        System.out.println("Arguments:");
        System.out.println("  <file>          Path to the text document to analyze\n");
        System.out.println("Options:");
        System.out.println("  -n <count>      Number of top keywords to return (default: 3)");
        System.out.println("  -s <count>      Number of top sentences per keyword (default: 1)");
        System.out.println("  -h, --help      Show this help message\n");
        System.out.println("Predefined Keywords:");
        for (int i = 0; i < VERIFICATION_KEYWORDS.size(); i++) {
            System.out.println("  " + (i + 1) + ". " + VERIFICATION_KEYWORDS.get(i));
        }
    }

    /**
     * Process a document file asynchronously with progress indicator
     */
    public void processFileAsync(String filePath, int numResults, int numTopSentences) {
        isProcessing = true;

        // Start the progress indicator in a separate thread
        CompletableFuture<Void> progressIndicator = CompletableFuture.runAsync(this::showProgressIndicator);

        // Process the file asynchronously
        CompletableFuture<SearchResults> processingFuture = CompletableFuture.supplyAsync(() -> 
            processFile(filePath, numResults, numTopSentences)
        );

        // When processing completes, stop the indicator and print results
        processingFuture
            .whenComplete((results, error) -> {
                isProcessing = false;
                
                // Give the progress indicator time to stop cleanly
                try {
                    progressIndicator.get(100, TimeUnit.MILLISECONDS);
                } catch (Exception ignored) {}
                
                // Clear the progress line
                System.out.print("\r" + " ".repeat(50) + "\r");
                System.out.flush();
                
                if (error != null) {
                    System.err.println("{\"error\": \"" + error.getMessage() + "\"}");
                    System.exit(1);
                } else if (results != null) {
                    printResults(results);
                }
            })
            .join(); // Wait for completion
    }

    /**
     * Show a spinning progress indicator while processing
     */
    private void showProgressIndicator() {
        String[] spinnerFrames = {"⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"};
        int frameIndex = 0;
        
        while (isProcessing) {
            System.out.print("\r" + spinnerFrames[frameIndex] + " Working on it...");
            System.out.flush();
            frameIndex = (frameIndex + 1) % spinnerFrames.length;
            
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }

    /**
     * Process a document file and find semantic keyword matches
     */
    public SearchResults processFile(String filePath, int numResults, int numTopSentences) {
        try {
            // Read file content
            String documentText = Files.readString(Path.of(filePath));
            return processContent(documentText, numResults, numTopSentences);
        } catch (IOException e) {
            throw new RuntimeException(e.getMessage(), e);
        }
    }

    /**
     * Split document into sentences using regex
     */
    private List<String> splitIntoSentences(String text) {
        // Pattern similar to Python version: split on sentence-ending punctuation
        // followed by whitespace, but avoid splitting on abbreviations
        String pattern = "(?<!\\w\\.\\w.)(?<![A-Z][a-z]\\.)(?<=\\.|\\?|!)\\s+";

        return Arrays.stream(text.trim().split(pattern))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .collect(Collectors.toList());
    }

    /**
     * Find semantic matches between keywords and document sentences
     */
    private SearchResults findSemanticMatches(
            List<String> sentences, List<double[]> sentenceEmbeddings,
            List<String> keywords, List<double[]> keywordEmbeddings,
            int numResults, int numTopSentences) {

        Map<String, KeywordMatch> keywordDetails = new LinkedHashMap<>();
        List<OverallMatch> overallBestMatches = new ArrayList<>();

        // For each keyword, find the most similar sentences
        for (int k = 0; k < keywords.size(); k++) {
            String keyword = keywords.get(k);
            double[] keywordEmb = keywordEmbeddings.get(k);

            // Calculate similarity to all sentences
            List<SentenceScore> sentenceScores = new ArrayList<>();
            for (int s = 0; s < sentences.size(); s++) {
                double similarity = cosineSimilarity(keywordEmb, sentenceEmbeddings.get(s));
                sentenceScores.add(new SentenceScore(sentences.get(s), similarity, s));
            }

            // Sort by similarity (descending - higher is better)
            sentenceScores.sort((a, b) -> Double.compare(b.similarity, a.similarity));

            // Take top N sentences
            List<SentenceScore> topSentences = sentenceScores.stream()
                    .limit(numTopSentences)
                    .collect(Collectors.toList());

            // Store keyword match details
            KeywordMatch match = new KeywordMatch();
            match.topMatchSentence = topSentences.isEmpty() ? "" : topSentences.get(0).sentence;
            match.topMatchSimilarity = topSentences.isEmpty() ? 0 : topSentences.get(0).similarity;
            match.allMatchedSentences = topSentences.stream()
                    .map(ss -> ss.sentence)
                    .collect(Collectors.toList());
            match.allSimilarities = topSentences.stream()
                    .map(ss -> ss.similarity)
                    .collect(Collectors.toList());

            keywordDetails.put(keyword, match);

            // Track for overall ranking
            if (!topSentences.isEmpty()) {
                overallBestMatches.add(new OverallMatch(
                        keyword,
                        topSentences.get(0).similarity,
                        topSentences.get(0).sentence));
            }
        }

        // Sort overall matches by similarity (descending)
        overallBestMatches.sort((a, b) -> Double.compare(b.similarity, a.similarity));

        // Get top N keywords overall
        List<OverallMatch> topKeywords = overallBestMatches.stream()
                .limit(numResults)
                .collect(Collectors.toList());

        return new SearchResults(topKeywords, keywordDetails);
    }

    /**
     * Calculate cosine similarity between two vectors
     */
    private double cosineSimilarity(double[] a, double[] b) {
        if (a.length != b.length) {
            throw new IllegalArgumentException("Vectors must have same length");
        }

        double dotProduct = 0.0;
        double normA = 0.0;
        double normB = 0.0;

        for (int i = 0; i < a.length; i++) {
            dotProduct += a[i] * b[i];
            normA += a[i] * a[i];
            normB += b[i] * b[i];
        }

        if (normA == 0 || normB == 0) {
            return 0.0;
        }

        return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
    }

    /**
     * Print results as JSON
     */
    private void printResults(SearchResults results) {
        System.out.println("\n✓ Analysis complete!\n");
        System.out.println("Top Matching Keywords:");
        System.out.println("=".repeat(50));
        
        for (int i = 0; i < results.topKeywords.size(); i++) {
            OverallMatch match = results.topKeywords.get(i);
            System.out.printf("%d. %s (similarity: %.4f)%n", 
                i + 1, match.keyword, match.similarity);
            System.out.printf("   Matched: \"%s\"%n%n", 
                truncate(match.matchedSentence, 60));
        }
        
        // Also output JSON format
      
        StringBuilder json = new StringBuilder();
        json.append("[\n");

        for (int i = 0; i < results.topKeywords.size(); i++) {
            OverallMatch match = results.topKeywords.get(i);
            json.append(match.keyword + ",");
        
            json.append("\n");
        }

        json.append("]");
        System.out.println(json);
    }

    private String truncate(String text, int maxLength) {
        if (text.length() <= maxLength) {
            return text;
        }
        return text.substring(0, maxLength - 3) + "...";
    }

    private String escapeJson(String text) {
        return text.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t");
    }

    // --- Inner Classes ---

    static class SentenceScore {
        String sentence;
        double similarity;
        int index;

        SentenceScore(String sentence, double similarity, int index) {
            this.sentence = sentence;
            this.similarity = similarity;
            this.index = index;
        }
    }

    static class KeywordMatch {
        String topMatchSentence;
        double topMatchSimilarity;
        List<String> allMatchedSentences;
        List<Double> allSimilarities;
    }

    static class OverallMatch {
        String keyword;
        double similarity;
        String matchedSentence;

        OverallMatch(String keyword, double similarity, String matchedSentence) {
            this.keyword = keyword;
            this.similarity = similarity;
            this.matchedSentence = matchedSentence;
        }
    }

    static class SearchResults {
        List<OverallMatch> topKeywords;
        Map<String, KeywordMatch> keywordDetails;

        SearchResults(List<OverallMatch> topKeywords, Map<String, KeywordMatch> keywordDetails) {
            this.topKeywords = topKeywords;
            this.keywordDetails = keywordDetails;
        }
    }
}

/**
 * Interface for embedding engines - allows swapping implementations
 */
interface EmbeddingEngine {
    void buildVocabulary(List<String> sentences, List<String> keywords);

    double[] embed(String text);
}

/**
 * TF-IDF based embedding engine - lightweight alternative to neural embeddings
 */
class TfIdfEmbeddingEngine implements EmbeddingEngine {

    private Map<String, Integer> vocabulary;
    private Map<String, Double> idfScores;
    private int vocabSize;

    @Override
    public void buildVocabulary(List<String> sentences, List<String> keywords) {
        // Combine all texts
        List<String> allTexts = new ArrayList<>();
        allTexts.addAll(sentences);
        allTexts.addAll(keywords);

        // Build vocabulary from all unique terms
        Set<String> terms = new HashSet<>();
        Map<String, Integer> docFreq = new HashMap<>();

        for (String text : allTexts) {
            Set<String> textTerms = tokenize(text);
            terms.addAll(textTerms);

            // Count document frequency
            for (String term : textTerms) {
                docFreq.merge(term, 1, Integer::sum);
            }
        }

        // Create vocabulary index
        vocabulary = new HashMap<>();
        int index = 0;
        for (String term : terms) {
            vocabulary.put(term, index++);
        }
        vocabSize = vocabulary.size();

        // Calculate IDF scores
        int totalDocs = allTexts.size();
        idfScores = new HashMap<>();
        for (Map.Entry<String, Integer> entry : docFreq.entrySet()) {
            double idf = Math.log((double) totalDocs / (1 + entry.getValue())) + 1;
            idfScores.put(entry.getKey(), idf);
        }
    }

    @Override
    public double[] embed(String text) {
        double[] embedding = new double[vocabSize];

        // Tokenize and count term frequencies
        List<String> tokens = new ArrayList<>(tokenize(text));
        Map<String, Long> termFreq = tokens.stream()
                .collect(Collectors.groupingBy(t -> t, Collectors.counting()));

        // Calculate TF-IDF for each term
        for (Map.Entry<String, Long> entry : termFreq.entrySet()) {
            String term = entry.getKey();
            if (vocabulary.containsKey(term)) {
                int idx = vocabulary.get(term);
                double tf = 1 + Math.log(entry.getValue()); // Log-scaled TF
                double idf = idfScores.getOrDefault(term, 1.0);
                embedding[idx] = tf * idf;
            }
        }

        // L2 normalize the embedding
        double norm = 0;
        for (double v : embedding) {
            norm += v * v;
        }
        if (norm > 0) {
            norm = Math.sqrt(norm);
            for (int i = 0; i < embedding.length; i++) {
                embedding[i] /= norm;
            }
        }

        return embedding;
    }

    private Set<String> tokenize(String text) {
        // Simple tokenization: lowercase, remove punctuation, split on whitespace
        return Arrays.stream(text.toLowerCase()
                .replaceAll("[^a-zA-Z0-9\\s]", " ")
                .split("\\s+"))
                .filter(s -> !s.isEmpty() && s.length() > 1)
                .collect(Collectors.toSet());
    }
}