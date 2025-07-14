import java.util.regex.Matcher; 
import java.util.regex.Pattern;

public class PalindromeChecker {

    /**
     * Reverses a given string.
     *
     * @param str The string to reverse.
     * @return The reversed string, or null if the input is null or empty.
     */
    public static String reverseString(String str) {
        if (str == null || str.isEmpty()) {
            return null;
        }
        return new StringBuilder(str).reverse().toString();
    }

    /**
     * Checks if a string is a palindrome (ignoring case and non-alphanumeric characters).
     *
     * @param str The string to check.
     * @return True if the string is a palindrome, false otherwise.
     */
    public static boolean isPalindrome(String str) {
        if (str == null || str.isEmpty()) {
            return false;
        }

        // Remove non-alphanumeric characters and convert to lowercase
        String cleanStr = str.replaceAll("[^a-zA-Z0-9]", "").toLowerCase();
        
        String reversedStr = reverseString(cleanStr);
        return cleanStr.equals(reversedStr);
    }

    public static void main(String[] args) {
        if (args.length == 0) {
            System.out.println("Please provide a string as a command-line argument.");
            return;
        }

        String inputString = args[0];
        boolean isPal = isPalindrome(inputString);
        System.out.println("Input String: \"" + inputString + "\"\nIs Palindrome: " + isPal);
    }
}