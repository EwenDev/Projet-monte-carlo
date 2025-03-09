import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

/**
 * Approximates PI using the Monte Carlo method.  Demonstrates
 * use of Callables, Futures, and thread pools.
 */
class Pi
{
	public static void main(String[] args) throws Exception
	{
		long total=0;
		// 10 workers, 50000 iterations each
		long totalCount = args[0].equals("") ? 50000 : Long.parseLong(args[0]);
		int numWorkers = args[1].equals("") ? 10 : Integer.parseInt(args[1]);
		String outname = args[2].equals("") ? "../out_pi.txt" : args[2];
		total = new Master().doRun(totalCount, numWorkers, outname);
		System.out.println("total from Master = " + total);
	}
}

/**
 * Creates workers to run the Monte Carlo simulation
 * and aggregates the results.
 */
class Master {
	public long doRun(long totalCount, int numWorkers,  String outname) throws InterruptedException, ExecutionException
	{

		long startTime = System.currentTimeMillis();

		// Create a collection of tasks
		List<Callable<Long>> tasks = new ArrayList<Callable<Long>>();
		for (int i = 0; i < numWorkers; ++i)
		{
			tasks.add(new Worker(totalCount/numWorkers));
		}

		// Run them and receive a collection of Futures
		ExecutorService exec = Executors.newFixedThreadPool(numWorkers);
		List<Future<Long>> results = exec.invokeAll(tasks);
		long total = 0;

		// Assemble the results.
		for (Future<Long> f : results)
		{
			// Call to get() is an implicit barrier.  This will block
			// until result from corresponding worker is ready.
			total += f.get();
		}
		double pi = 4.0 * total / totalCount;

		long stopTime = System.currentTimeMillis();

		System.out.println("\nPi : " + pi );
		System.out.println("Error: " + (Math.abs((pi - Math.PI)) / Math.PI) +"\n");

		System.out.println("Ntot: " + totalCount);
		System.out.println("Available processors: " + numWorkers);
		System.out.println("Time Duration (ms): " + (stopTime - startTime) + "\n");

		System.out.println( (Math.abs((pi - Math.PI)) / Math.PI) +" "+ totalCount*numWorkers +" "+ numWorkers +" "+ (stopTime - startTime));

		String data = "\n"+totalCount +", " + Math.abs(pi - Math.PI) / Math.PI +", " + numWorkers +", " + (stopTime - startTime);

		FileWriter writer = null;
		try {
			writer = new FileWriter(outname,true);
			writer.write(data);
			writer.close();
		} catch (IOException e) {
			throw new RuntimeException(e);
		}


		exec.shutdown();
		return total;
	}
}

/**
 * Task for running the Monte Carlo simulation.
 */
class Worker implements Callable<Long>
{
	private final long numIterations;
	public Worker(long num)
	{
		this.numIterations = num;
	}

	@Override
	public Long call()
	{
		long circleCount = 0;
		Random prng = new Random ();
		for (int j = 0; j < numIterations; j++)
		{
			double x = prng.nextDouble();
			double y = prng.nextDouble();
			if ((x * x + y * y) < 1)  ++circleCount;
		}
		return circleCount;
	}
}