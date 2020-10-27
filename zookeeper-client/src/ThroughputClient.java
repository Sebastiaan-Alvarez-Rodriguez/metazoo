import org.apache.log4j.Logger;
import org.apache.zookeeper.AsyncCallback;
import org.apache.zookeeper.KeeperException;
import org.apache.zookeeper.ZooKeeper;
import org.apache.zookeeper.data.Stat;

import java.io.FileWriter;
import java.io.IOException;

//a Zookeeper client to test the throughput of a Zookeeper cluster
//does not quit automatically
public class ThroughputClient {
    private static String logfile;
    private static int operations;
    private static ZooKeeperConnection conn;
    private static ZnodeManager nodes;
    private static String node_name;
    private static Logger LOG;

    private static int NR_READS;
    private static int NR_WRITES;
    private static final int OUTGOING = 100;
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

        for (int i = 0; i < NR_READS; ++i)
            nodes.getData_async(node_name, db);
        for (int i = 0; i < NR_WRITES; ++i)
            nodes.setData_async(node_name, data, sb);

        //waiting for process to be quit
        while (true) ;
    }

    //if client gets killed, do a clean-up and log all counted operations (by appending)
    public static void shutdown() {
        try {
            nodes.delete(node_name);
            conn.close();
        } catch (Exception ignored) {
            //LOG.error(e.getMessage());
        }
        try {
            FileWriter writer = new FileWriter(logfile, true);
            writer.write(NR_READS +","+operations+"\n");
            writer.close();
        } catch (IOException ignored) {
            //LOG.error(e.getMessage());
        }
    }

    public static void main(String[] args) {
        if (args.length != 4) {
            System.out.println("[CLIENT] [ERROR] expected four arguments");
            System.exit(1);
        }
        String host = args[0];
        int id = Integer.parseInt(args[1]);
        logfile = args[2];
        NR_READS = Integer.parseInt(args[3]);
        NR_WRITES = OUTGOING - NR_READS;
        operations = 0;
        conn = new ZooKeeperConnection();
        try {
            LOG = Logger.getLogger(ThroughputClient.class);
            node_name = "/ClientNode" + id;
            String message = "I am Client"+ id;
            LOG.warn(message);
            Runtime.getRuntime().addShutdownHook(new Thread(ThroughputClient::shutdown));
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
