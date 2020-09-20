# Zookeeper
This file lists several steps to follow when making this project

## STEP 1
 - [ ] Read your chosen article carefully, trying to understand what experiments the authors have designed and why. 
 - [ ] Write in your report what experiments you identified in the article, what was the goal of the experiments, how they were conducted, on which kind of infrastructure, what dataset, what scale (number of machines), how many times experiments were repeated, what statistical methods were applied.

### Concerns/Ideas:
 1. *"The implementation is publicly available [here](http://hadoop.apache.org/zookeeper)"*
 2. *"ZooKeeper seems to be Chubby without the lockmethods"*.  
Chubby is named very often, but I only saw one comparison, not even backed up by numbers.
 3. *"It is important to observe that all results that hold for linearizable objects also hold for A-linearizable objects because a system that satisfies A-linearizability also satisfies linearizability"*.  
Uhm? Is it not the other way around then?
 4. I expected multiple (types of) primitives in experiments, but I believe they did not do that. They gave a reason, but I wonder if they should have done it... They also seem to give a reason without experiments to back it up.
 5. since they replicate a lot, I wondered about memory, but this does not seem to be addressed.
 6. *"Each znode in the tree stores amaximum of 1MB of data by default, but this maximumvalue is a configuration parameter that can be changed inspecific cases."*
 7. *"...ZooKeeper is more than 3 times higher than the published throughput of Chubby"*.  
I see no stats/ numbers?
 8. They often have no repetitions
 9. When they give average, they give nothing like standard deviation
 10. The number of clients/ servers deviate a lot between experiments. Cherry picking?

Implementations:
 - ZooKeeper (API)
 - Zab \[24\] (Broadcast Protocol)

All experiments (except perhaps first one):
 Infrastructure: Xeon dual-core 2.1 GHz processor, 4GB Ram, gigabit ethernet, 2 SATA hard drives.
 Scale: 50 servers

|Experiment|Goal|How|Dataset|repetitions|statistical methods|Scale (if different)|
|---|---|---|---|---|---|---|
|Figure 2|Workload for 3 days used by FS|count #operations every second|Fetching Service (Yahoo) (not really dataset)|1 (no reps)|frequencies?|?|
|Throughput|Measure Throughput for saturated systems or injected failures|java server to log to disk, snapshot to another. async Java client API 100 requests outstanding, with read or write of 1K data. Clients send counts of completed operations every 300 ms, they sample every 6s|?|1|frequencies?|35 machines to simulate 250 simultaneous clients|
|Throughput 2|Show what happens if using no relaxation and force clients to only connect to leader|Use no relaxation|...|1|frequencies|-|
|Atomic Broadcast|Measure Atomic Broadcast throughput|simulate clients by generating transactions directly to leader|...|1|Average + min, max value|-|
|Failures|Measure Throughput when Failures|Use same saturation benchmark, but keep write percentage at constant 30%. Periodically kill some of server processes|...|1|Frequencies|5 machines|
|Latency|Assess latency of requests|worker process sends a create, waits for finish, sends asynchronous delete and starts new create. Each worker creates 50 000 nodes.|...|1|throughput = no. requests completed / total time to complete|3, 5, 7, 9 servers combined with 1, 10, 20 workers|
|Barriers|Measures performance of barriers|each client enters all b barriers, en then leaves all of them|..|5|Average|50, 100, 200 clients|



## STEP 2
 - [ ] Pick two of these experiments. 
 - [ ] Write in your report why you chose them, why they are significant, where do you think the authors are wrong in their design, what you plan to do differently and why. (If you would not design the experiments differently, explain why.)

|Experiment|Why|Significance|Design Mistakes|New|
|---|---|---|---|---|
|?|?|?|?|?|

## STEP 3
 - [ ] Run the two experiments in DAS-5. 
    - Develop scripts to allocate and de-allocate nodes, 
    - develop scripts to run your experiments on the allocated nodes. 
    - Run the two experiments in two ways: 
        - (1) as the original authors described them; 
        - (2) as you describe at point 2). (In case you would not change the design of the experiments, you do not need to run the 2nd experiment.) 
 - [ ] Write in your report the choice of parameters for the experiments and how you designed your deployment and running scripts.

## STEP 4
 - [ ] Analyze the results you achieved. 
 - [ ] Write in your report whether the results you achieved are different to those of the authors and explain why. 
 - [ ] Draw graphs showing your results. (NB: similar results do not mean exactly matching the numbers the authors show, this is impossible, as the hardware is different. However, similar results mean similar trends, e.g., “system X is faster than system Y”, “system A is scaling linearly”.)

## STEP 5
 - [ ] Pack all your code and report (in pdf format) into a tarball, and upload it to Brightspace