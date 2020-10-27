import java.io.IOException; 
import java.util.concurrent.CountDownLatch; 

import org.apache.zookeeper.WatchedEvent;
import org.apache.zookeeper.Watcher;
import org.apache.zookeeper.Watcher.Event.KeeperState;
import org.apache.zookeeper.ZooKeeper;

//class to set up and close a Zookeeper connection
public class ZooKeeperConnection {
	private ZooKeeper zoo; 
	final CountDownLatch connectedSignal = new CountDownLatch(1); 

	//connect to Zookeeper through address 'host'
	public ZooKeeper connect(String host) throws IOException, InterruptedException {
		zoo = new ZooKeeper(host, 50000, new Watcher() {
			public void process(WatchedEvent we) {
				if (we.getState() == KeeperState.SyncConnected) {
					connectedSignal.countDown();
				}
			}
		}); 

		connectedSignal.await(); 
		return zoo;
	}

	//close the Zookeeper connection
	public void close() throws InterruptedException {
		zoo.close();
	}

}