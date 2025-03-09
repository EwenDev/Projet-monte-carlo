package assignments;

import java.io.*;
import java.net.*;

public class WorkerSocket {
    static int port = 25545; // port par défaut
    private static boolean isRunning = true;

    public static void main(String[] args) throws Exception {
        if(args.length > 0 && !args[0].isEmpty()){
            port = Integer.parseInt(args[0]);
        }
        ServerSocket serverSocket = new ServerSocket(port);
        System.out.println("WorkerSocket démarré sur le port " + port);
        Socket socket = serverSocket.accept();

        BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        PrintWriter out = new PrintWriter(new BufferedWriter(new OutputStreamWriter(socket.getOutputStream())), true);

        String line;
        while (isRunning && (line = in.readLine()) != null) {
            if(!line.equals("END")){
                System.out.println("Reçu, itérations = " + line);
                int iterations = Integer.parseInt(line);
                int count = computeMonteCarlo(iterations);
                out.println(count);
            } else {
                isRunning = false;
            }
        }
        in.close();
        out.close();
        socket.close();
        serverSocket.close();
    }

    private static int computeMonteCarlo(int iterations) {
        int count = 0;
        for (int i = 0; i < iterations; i++){
            double x = Math.random();
            double y = Math.random();
            if (x * x + y * y <= 1)
                count++;
        }
        return count;
    }
}
