# aws-app-bucket-sync

The aws-app-bucket-sync is the application challenge just to describe how to run one tier aplication getting data from a mongo database render a js Page using the Flask to render variables and getting requests to sync Object bettewn AWS Buckets 




####
![AWS Architecture Diagram challenge](imgs/challenge-aws.jpg?raw=true "Diagram")



## Describe Architecture 

```
ECS AWS - WORKERS 
    worker 1 with ENV VARS POSTGRESS_DB_HOST, MONGO_DB_HOST
    worker 2 with ENV VARS POSTGRESS_DB_HOST, MONGO_DB_HOST
    worker 3 with ENV VARS POSTGRESS_DB_HOST, MONGO_DB_HOST
    web    4 with ENV VARS POSTGRESS_DB_HOST, MONGO_DB_HOST
EC2 - DB 
    mongo_db  on container 
    postgress_db on container 


ASG - AUTO SCALING GROUP -FRONT ECS 
    web linux img 2 instances tipe t2 
ELB -  TO PROVIDE DB ACCESS 
    expose postgres db port 
    expose mongodb port 

WEB       - CONNECT ON MONGO DB AND GET INFOS FROM ALL BUCKETS 
WORKER 1  - GET ALL OBJECTS NAMES FROM BUCKETS ON BUCKET LIST PARAMETER EM INSERT INFOS ON POSTGRESS DATABASE 
WORKER 2  - GET INFOS FROM POSTRGRESS DATABASE AND INSERT INFOS ON MONGO COLLECTIONS 
WORKER 3  - GET REQUEST_SYNC FROM POSTGRESS DATABASE AND START A SYNC OBJECT 

```
 ## Ec2 instances Type : 
For this challeng we choice just ec2  t2.micro type for: <br />
* Database servers. 
* Ecs Instance servers. 

    

 ## Cluster Ecs 
 Cluster is created using container instances (EC2 launch type, not Fargate!).
 In this example, verified module `vpc` is imported from Terraform Registry, other resources are created in relevant files.
 In file `ecs.tf` we create:
  - cluster of container instances _web-cluster_
  - capacity provider, which is basically AWS Autoscaling group for EC2 instances. In this example managed scaling is enabled, Amazon ECS manages the scale-in and scale-out actions of the Auto Scaling group used when creating the capacity provider. I set target capacity to 85%, which will result in the Amazon EC2 instances in your Auto Scaling group being utilized for 85% and any instances not running any tasks will be scaled in.
  - task definition with family _web-family_, volume and container definition is defined in the file container-def.json
  - service _web-service_, desired count is set to 10, which means there are 10 tasks will be running simultaneously on your cluster. There are two service scheduler strategies available: REPLICA and DAEMON, in this example REPLICA is used. Application load balancer is attached to this service, so the traffic can be distributed between those tasks.
  Note: The _binpack_ task placement strategy is used, which places tasks on available instances that have the least available amount of the cpu (specified with the field parameter).

In file `asg.tf` we create:
  - launch configuration
  - key pair
  - security groups for EC2 instances
  - auto-scaling group.

**Note:** in order to enable ECS managed scaling you need to enable `protect from scale in` from auto-scaling group.

In file `iam.tf` we create roles, which will help us to associate EC2 instances to clusters, and other tasks.

In file `alb.tf` we create Application Load Balancer with target groups, security group and listener.   
## Database Servers 
    The Database servers  are running on Ec2 instances and using elastic load balance for balance Session beteewn instances and provide more scales 
## How to Deploy 


 ```
    git clone repo : 
    git https://github.com/jefferson22alcantara/aws-app-bucket-sync.git
    cd aws-app-bucket-sync 
    git checkout -b 'PR_REQUEST_0.0.1'
    echo "PR_REQUEST_0.0.1" >> CHANGELOG.md 
    git commit -a -m 'PR_REQUEST_0.0.1'
    git push origin PR_REQUEST_0.0.1  
    [PR_REQUEST_0.0.1 5d94c7f] PR_REQUEST_0.0.1
    1 file changed, 1 insertion(+)
```
Open Pull request </br>
![pull request ](imgs/pull_request.jpg?raw=true "Diagram")


Waiting for terraform Plan result</br>
![Project Home ](imgs/projetc_home.jpg?raw=true "Diagram")

Getting the Url from elb  output and open on your browser : </br>

![Project Home ](imgs/projetc_home.jpg?raw=true "Diagram")


Select bucket :aws-app-bucket-sync-11   and client on list bucket button </br>

Click on sync button and choice or destination bucket 
![select ](imgs/projetc_home.jpg?raw=true "Diagram")



## Contributing

See https://github.com/jefferson22alcantara/aws-app-bucket-sync


[1]: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/clusters.html

[2]: https://github.com/jefferson22alcantara/aws-app-bucket-sync