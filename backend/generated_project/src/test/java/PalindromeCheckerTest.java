import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class PalindromeCheckerTest {

    @Test
    void testReverseString() {
        assertEquals("cba", PalindromeChecker.reverseString("abc"));
        assertEquals("A man, a plan, a canal: Panama", PalindromeChecker.reverseString("Panama: a canal, a plan, a man, A"));
        assertNull(PalindromeChecker.reverseString(null));
        assertNull(PalindromeChecker.reverseString(""));
    }

    @Test
    void testIsPalindrome() {
        assertTrue(PalindromeChecker.isPalindrome("madam"));
        assertTrue(PalindromeChecker.isPalindrome("racecar"));
        assertTrue(PalindromeChecker.isPalindrome("A man, a plan, a canal: Panama"));
        assertFalse(PalindromeChecker.isPalindrome("hello"));
        assertFalse(PalindromeChecker.isPalindrome(null));
        assertFalse(PalindromeChecker.isPalindrome(""));
        assertTrue(PalindromeChecker.isPalindrome("12321"));
        assertFalse(PalindromeChecker.isPalindrome("12345"));
    }
}