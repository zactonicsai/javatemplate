package zac.example.lib;

public interface DocConverter {
    void convert(String input, String output);
    String getSupportedType(); // optional: to identify the converter
}
