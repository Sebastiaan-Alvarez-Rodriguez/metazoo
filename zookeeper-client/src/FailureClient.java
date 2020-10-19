import org.apache.log4j.Logger;
import org.apache.zookeeper.AsyncCallback;
import org.apache.zookeeper.KeeperException;
import org.apache.zookeeper.ZooKeeper;
import org.apache.zookeeper.data.Stat;

import java.util.LinkedList;
import java.util.Timer;
import java.util.TimerTask;

public class FailureClient {
    private static ZnodeManager nodes;
    private static int operations;
    private static final LinkedList<Integer> ops = new LinkedList<Integer>();
    private static Timer timer;
    private static String node_name;
    private static volatile boolean CONTINUE = true;

    private static final int NR_READS = 70;
    private static final int NR_WRITES = 30;
    private static final int BYTES = 1024;

    public static void run() throws KeeperException, InterruptedException {
           byte[] data = new byte[BYTES];
           for (int i = 0; i < BYTES; ++i)
               data[i] = (byte)i;

           if (!nodes.exists(node_name))
               nodes.create(node_name, data);

           class MyDataCallback implements AsyncCallback.DataCallback {
               @Override
               public void processResult(int rc, String path, Object ctx, byte[] data, Stat stat) {
                   ++operations;
                   nodes.getData_async(node_name, this);
               }
           }

           class MyStatCallback implements AsyncCallback.StatCallback {
               @Override
               public void processResult(int rc, String path, Object ctx, Stat stat) {
                   try {
                       ++operations;
                       nodes.setData_async(node_name, data, this);
                   } catch (Exception e) {
                       System.out.println(e.getMessage());
                       CONTINUE = false;
                   }
               }
           }

           MyDataCallback db = new MyDataCallback();
           MyStatCallback sb = new MyStatCallback();

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

           //waiting for servers to quit
           while (CONTINUE);
    }

    public static void main(String[] args)  {
        if (args.length != 2) {
            System.out.println("[ERROR] expected two arguments");
            System.exit(1);
        }
        Logger LOG = Logger.getLogger(FailureClient.class);
        String host = args[0];
        int id = Integer.parseInt(args[1]);
        node_name = "/ClientNode" + id;
        String message = "I am Client"+ Integer.toString(id);
        LOG.warn(message);
        operations = 0;
        ZooKeeperConnection conn = new ZooKeeperConnection();
        try {
            ZooKeeper zoo = conn.connect(host);
            nodes = new ZnodeManager(zoo);
            run();
        } catch (Exception e) {
            System.out.println(e.getMessage());
        } finally {
            //Chose WARN level so we can turn off INFO
            try {
                nodes.delete(node_name);
                conn.close();
            } catch (Exception e) {
                System.out.println(e.getMessage());
            }
            timer.cancel();
            timer.purge();
            for(Integer i : ops)
                LOG.warn("ops: "+i.toString());
        }


    }
}