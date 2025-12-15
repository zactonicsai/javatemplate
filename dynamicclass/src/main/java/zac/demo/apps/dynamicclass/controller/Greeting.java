package zac.demo.apps.dynamicclass.controller;

public class Greeting {
    private String message;
    private int id;

    // Constructor
    public Greeting(int id, String message) {
        this.id = id;
        this.message = message;
    }

    // Getters are required for JSON serialization
    public int getId() {
        return id;
    }

    public String getMessage() {
        return message;
    }
}
