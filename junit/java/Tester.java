import java.util.List;

import org.junit.Test;
import org.junit.runner.JUnitCore;
import org.junit.runner.Result;
import org.junit.runner.notification.Failure;

import static org.junit.Assert.*;

public class Tester {

	// place raw code here
	%(solution)s		
	
	@Test
	public void testHelloWorld() {
		
		// place test code here
		%(tests)s
	}
	
	public static void main(String args[]) {
		Class<?> myClass = new Object(){}.getClass().getEnclosingClass();
		Result result = JUnitCore.runClasses(myClass);
		List<Failure> failures = result.getFailures(); 
		
		for (Failure failure : failures) {
			System.out.println("[FAILED] " + failure.getMessage());
		}		
	}

}
