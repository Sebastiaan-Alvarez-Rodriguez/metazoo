import org.apache.log4j.Logger;
import org.apache.zookeeper.AsyncCallback;
import org.apache.zookeeper.KeeperException;
import org.apache.zookeeper.ZooKeeper;
import org.apache.zookeeper.data.Stat;

import java.io.FileWriter;
import java.io.IOException;
import java.util.LinkedList;
import java.util.Timer;
import java.util.TimerTask;


//a Zookeeper client to test the fault-tolerance of a Zookeeper cluster
//for a fixed read/write (70/30) ratio
//does not quit automatically
public class FailureClient {
    private static ZnodeManager nodes;
    private static int operations;
    private static final LinkedList<Integer> ops = new LinkedList<>();
    private static Timer timer;
    private static String node_name;
    private static ZooKeeperConnection conn;
    private static Logger LOG;
    private static String logfile;

    private static final int NR_READS = 70;
    private static final int NR_WRITES = 30;
    private static final int BYTES = 1024;

    public static void run() throws KeeperException, InterruptedException {
           byte[] data = new byte[BYTES];
           for (int i = 0; i < BYTES; ++i)
               data[i] = (byte)i;

           if (!nodes.exists(node_name))
               nodes.create(node_name, data);

           //if read request succeeded, resend the request
           class MyDataCallback implements AsyncCallback.DataCallback {
               @Override
               public void processResult(int rc, String path, Object ctx, byte[] data, Stat stat) {
                   ++operations;
                   nodes.getData_async(node_name, this);
               }
           }

           //if write request succeeded, resend the request
           class MyStatCallback implements AsyncCallback.StatCallback {
               @Override
               public void processResult(int rc, String path, Object ctx, Stat stat) {
                   try {
                       ++operations;
                       nodes.setData_async(node_name, data, this);
                   } catch (Exception ignored) {
                       //LOG.error(e.getMessage());
                   }
               }
           }

           MyDataCallback db = new MyDataCallback();
           MyStatCallback sb = new MyStatCallback();

           //log the operations for each 300ms
           timer = new Timer();
           timer.scheduleAtFixedRate(new TimerTask() {
               @Override
               public void run() {
                    ops.add(operations);
                    operations = 0;
               }
           }, 300, 300);

           for (int i = 0; i < NR_READS; ++i)
               nodes.getData_async(node_name, db);
           for (int i = 0; i < NR_WRITES; ++i)
               nodes.setData_async(node_name, data, sb);

           //waiting for process to be quit
           while (true) ;
    }

    //if client gets killed, do a clean-up and log the last operations
    public static void shutdown() {
        try {
            nodes.delete(node_name);
            conn.close();
        } catch (Exception e) {
            LOG.error(e.getMessage());
        }
        if (timer != null) {
            timer.cancel();
            timer.purge();
        } else {
            System.out.println("[CLIENT] [ERROR] Unexpected Error");
        }
        try {
            FileWriter writer = new FileWriter(logfile);
            for(Integer i : ops)
                writer.write("ops: "+i.toString()+"\n");
            writer.close();
        } catch (IOException ignored) {
            //LOG.error(e.getMessage());
        }
    }

    public static void main(String[] args)  {
        if (args.length != 3) {
            System.out.println("[CLIENT] [ERROR] expected three arguments");
            System.exit(1);
        }

        String host = args[0];
        int id = Integer.parseInt(args[1]);
        logfile = args[2];
        operations = 0;
        conn = new ZooKeeperConnection();
        try {
            LOG = Logger.getLogger(FailureClient.class);
            node_name = "/ClientNode" + id;
            String message = "I am Client"+ id;
            LOG.warn(message);
            Runtime.getRuntime().addShutdownHook(new Thread(FailureClient::shutdown));
            ZooKeeper zoo = conn.connect(host);
            nodes = new ZnodeManager(zoo);
            run();
        } catch (Exception e) {
            LOG.error(e.getMessage());
        } finally {
            shutdown();
        }
    }
}
