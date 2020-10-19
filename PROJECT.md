# Zookeeper
This file lists several steps to follow when making this project.  
The implementation is publicly available [here](http://hadoop.apache.org/zookeeper).
Documentation of the implementation is [here](https://zookeeper.apache.org/doc/r3.3.2/zookeeperAdmin.html).  
The paper is available [here](https://static.usenix.org/event/atc10/tech/full_papers/Hunt.pdf).  
Chubby paper is available [here](https://static.googleusercontent.com/media/research.google.com/en//archive/chubby-osdi06.pdf).

## STEP 1
 - [x] Read your chosen article carefully, trying to understand what experiments the authors have designed and why. 
 - [X] Write in your report what experiments you identified in the article, what was the goal of the experiments, how they were conducted, on which kind of infrastructure, what dataset, what scale (number of machines), how many times experiments were repeated, what statistical methods were applied.

### Concerns/Ideas:
 1. *"ZooKeeper seems to be Chubby without the lockmethods"*.  
Chubby is named very often, but I only saw one comparison, not even backed up by numbers.
 2. *"It is important to observe that all results that hold for linearizable objects also hold for A-linearizable objects because a system that satisfies A-linearizability also satisfies linearizability"*.  
Uhm? Is it not the other way around then? **No, they state it correctly here**.
 3. I expected multiple (types of) primitives in experiments, but I believe they did not do that. They gave a reason, but I wonder if they should have done it... They also seem to give a reason without experiments to back it up.
 4. since they replicate a lot, I wondered about memory, but this does not seem to be addressed. 
    *"Each znode in the tree stores amaximum of 1MB of data by default, but this maximumvalue is a configuration parameter that can be changed inspecific cases."*
 5. *"...ZooKeeper is more than 3 times higher than the published throughput of Chubby"*.  
I see no stats/ numbers?
 6. They often have no repetitions
 7. When they give average, they give nothing like standard deviation
 8. The number of clients/ servers deviate a lot between experiments. Cherry picking?
 9. In figures 5/6 we are given a few lines showing throughput of the system with a varying percentage of read an write requests, where each line represents an amount of servers. It is unclear how each datapoint is formed: E.g. at '3 servers' line with 40% read requests the throughput is some number X. Is X the average? The highest value measured? If X is the average, what is the *variance* of the measurements?
 10. Table 1 gives some throughput performance statistics, but fails to mention whether it is an average amount of operations per second, or median, or just the best/worst measurements, and does not tell anything about variance
 11. In figure 7, we see the performance of broadcast halves when having a system scaling from 2 to 13 server nodes. Authors argue later on that there is CPU contention, since also serialization, client communication, ACL checks etc require CPU. This leads to think their system does not scale well when applied on a production-base with hundreds of servers. When thinking about it, the authors do not tell anything about the scalability of their system.
 12. In section 5.2, authors state they measure latency of requests with their own benchmark. It is not good practice to evaluate how well your framework works on your own benchmark
 13. Table 2 has 'create' requests per second, but does not tell if this is average, best results, worst results...
 14. Table 3 gives average time per second, but nothing on variance
 

Implementations:
 - ZooKeeper (API)
 - Zab \[24\] (Broadcast Protocol)

All experiments (except perhaps first one):
 Infrastructure: Xeon dual-core 2.1 GHz processor, 4GB Ram, gigabit ethernet, 2 SATA hard drives.
 Scale: 50 servers

|Experiment|Goal|How|Dataset|repetitions|statistical methods|Scale (if different)|
|---|---|---|---|---|---|---|
|Workload|Workload for 3 days used by FS|count #operations every second|Fetching Service (Yahoo) (not really dataset)|0 (no reps)|frequencies|?|
|Throughput|Measure Throughput for saturated systems or injected failures|java server to log to disk, snapshot to another. async Java client API 100 requests outstanding, with read or write of 1K data. Clients send counts of completed operations every 300 ms, they sample every 6s|?|0|Not given|35 machines to simulate 250 simultaneous clients|
|Throughput 2|Show what happens if using no relaxation and force clients to only connect to leader|Use no relaxation|?|0|frequencies|Presumably the same as 'Throughput' experiment|
|Atomic Broadcast|Measure Atomic Broadcast throughput|simulate clients by generating transactions directly to leader|?|0|Average and min, max|-|
|Failures|Measure Throughput when Failures|Use same saturation benchmark, but keep write percentage at constant 30%. Periodically kill some of server processes|?|0|None|5 machines|
|Latency|Assess latency of requests|worker process sends a create, waits for finish, sends asynchronous delete and starts new create. Each worker creates 50.000 nodes|Their own fabrication|0|throughput = #requests completed / total time to complete|3, 5, 7, 9 servers combined with 1, 10, 20 workers|
|Barriers|Measures performance of barriers|each client enters all b barriers, en then leaves all of them|?|4|Average|50, 100, 200 clients|



## STEP 2
 - [X] Pick two of these experiments.  
Experiments picked: **Failures** and **Latency**.
 - [X] Write in your report why you chose them, why they are significant, where do you think the authors are wrong in their design, what you plan to do differently and why. (If you would not design the experiments differently, explain why.)

|Experiment|Why|Significance|Design Mistakes|New|
|---|---|---|---|---|
|Failures|Interesting topic, but experiment was poor|Failures are unavoidable, thus knowing how a system reacts is crucial | No repetitions, thus very short time period. Only used 5 machines without any explanation. No statistical methods. | Run with multiple amounts of machines, repeat experiment [20-100] times and use statistical methods; use time delta to measure impact using median (perhaps bimodal since we have different situations), and percentiles |
|Latency|Least trustworthy and boldest statements|Latency is used most often to test these systems, so having good experiments is essential| Authors used own benchmark, they compare with other benchmark. No information on Chubby. They assumed every worker is equal in speed. No repetitions. No statistical methods. | Find a good benchmark or use the one for Chubby. Run the Chubby experiment on our own under same circumstances as ZooKeeper. 'Average' throughput per worker (with stdev and/or percentiles). Repeat experiment [20-100] times. |

## STEP 3
 - [ ] Run the two experiments in DAS-5. 
    <!--- [ ] Develop scripts to allocate and de-allocate nodes, -->
    1. Write script to allocate nodes with preserve
    2. Write script which fetches ip adresses for allocated nodes (e.g. ip adress of 'node112')
    3. Think of a way to install zookeeper on nodes
    4. Think of a way to tell zookeeper instances were the other instances live
    <!--- [ ] develop scripts to run your experiments on the allocated nodes. -->
    - [ ] Run the two experiments in two ways: 
        - [ ] (1) as the original authors described them; 
        - [ ] (2) as you describe at point 2). (In case you would not change the design of the experiments, you do not need to run the 2nd experiment.) 
 - [ ] Write in your report the choice of parameters for the experiments and how you designed your deployment and running scripts.

## STEP 4
 - [ ] Analyze the results you achieved. 
 - [ ] Write in your report whether the results you achieved are different to those of the authors and explain why. 
 - [ ] Draw graphs showing your results. (NB: similar results do not mean exactly matching the numbers the authors show, this is impossible, as the hardware is different. However, similar results mean similar trends, e.g., “system X is faster than system Y”, “system A is scaling linearly”.)

## STEP 5
 - [ ] Pack all your code and report (in pdf format) into a tarball, and upload it to Brightspace