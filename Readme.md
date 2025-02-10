# Integrating Generative AI and IoT Technologies

This repo is a demonstration of integrating Generative AI and IoT Technologies where a Gen AI Agent can read the live data from IoT and reason with it as per its knowledge base and help the Industry Maintenance Engineers.

## Scenario:
A company in the wind energy industry is facing several challenges in managing and maintaining the wind turbines that generate clean and sustainable power. One of these challenges is the shortage of expert engineering resources at many wind farm sites, especially in remote and rural areas. This leads to lower efficiency and reliability of the wind turbines, higher operational and maintenance costs, and increased environmental risks due to potential failures and accidents. Moreover, the local control systems that monitor the wind turbines are often outdated and incompatible, making it difficult to collect and analyse data across different sites and regions.

## Solution:
- Wind Turbine PLCs data will be simulated in Kepware OPC UA Server with simulation driver.
- Once Simulation Channel for each Wind Farm with multiple Wind Turbines will be implemented.
- The Simulation of Wind Farms and OPC UA is implemented in a Windows EC2 Instance.
- IoT Greengrass Core device to collect data from OPC UA server will be implemented in same or different Windows EC2 instance.
- IoT Greengrass Device will push the wind farm data to IoT SiteWise Edge Gateway in the AWS Cloud.
- Wind Turbine Models and Assets with Wind Farm hierarchy will be implemented in IoT SiteWise and will be associated with the Edge Gateway data.
- An intelligent agent with Amazon Bedrock will be developed which can query the wind turbine data from IoT SiteWise.
- The Agent will interface with IoT SiteWise through Lambda Functions.
- Aurora PostgreSQL – Serverless Database is used as knowledge base for Amazon Bedrock Agent.

## Solution Architecture for Integrating IoT SiteWise and Generative AI
![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/architecture.png?raw=true)

## This Repo Contains the Following
- Kepware OPC Server Wind Farm Project file for Simulation Driver - Wind-Farm-Simulation-Demo.opf. This project contains 6 wind farms each with 10 wind turbines and each wind turbine controller is simulated with following 10 parameters which are referred as Tags in the OPC project:
  - ActivePower
  - AmbientTemp
  - BearingTemp
  - Energy
  - ErrorCode
  - ErrorStatus
  - GearBoxVibration
  - RotorSpeed
  - WindDirection
  - WindSpeed
- Wind Turbine Generator device file in Kepware OPC Server with parameters – WTG-01.csv (you don’t need this if you use above file, this is for individually importing parameters in Devices in OPC server)
- IoT-SiteWise Project File for importing - Wind-Farm-CMS-IoT-SiteWise.json. This contains the corresponding assets for the simulated wind farm.
- Wind Turbine Maintenance Guide for setting up knowledge base in Sample-Wind-Turbine-Maintenance-Guide.docx
- Code for Lambda functions and SAM template to setup them, these lambda functions are used by Agent Action Group.
- Sample Prompts file.

## Implementation and Setup

### Wind Farm Simulation Server with Kepware
1. Create an EC2 instance with Windows OS and connect it through RDP.

2. Register with Kepware and Download a demo version.

3. Install the Kepware OPC Server with Simulation Driver.

4. Once setup is done load the OPF project file downloaded from the repo. The project will look like below, one channel per wind farm.
![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/kepware-opc-project.png?raw=true)

5. You can expand each wind farm channel to see wind turbine generator devices and their parameters as below.
![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/kepware-wtg-tags.png?raw=true)

6. Setup OPC Configuration as below, you access it from taskbar right click Kepware Icon.
![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/kepware-access-opc-ua-config.png?raw=true)

![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/images/opc-ua-config-1.png?raw=true)

![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/images/opc-ua-config-2.png?raw=true)


### Setup - IoT SiteWise
1. Create an SiteWise Edge Gateway as described here. Download the Edge Gateway installer and upload it to the Windows EC2 Kepware OPC Server Instance. Execute the Gateway Installer, this will install the necessary certificate to communicate to SiteWise Edge Gateway on AWS.

2. In the IoT SiteWise Console under bulk operations use New Import to import the Project JSON file from the repo.

3. This will create Models and Assets. A Central Monitoring System – CMS model with All Wind Farms, A Wind Farm Model with all the Wind Turbine Generators – WTG and a WTG Model.
![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/iot-sitewise-cms.png?raw=true)

4. In the Edge Gateway Add Data Sources as below.
![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/edge-gateway-config-1.png?raw=true)

![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/edge-gateway-config-2.png?raw=true)

![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/edge-gateway-config-3.png?raw=true)

5. Setup Property Groups in Advanced Configuration for all the wind farms.

6. Once Data Sources are added and Synced the Configuration status will show In Sync.

7. You can also observe the Edge Gateway is connect to OPC Server as a client in the Simulator Instance as below – Client 1 Active Tags.
![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/kepware-active-client.png?raw=true)

8. Also Observe Data being Pushed to IoT SiteWise as below and MQTT Notification as Active.
![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/iot-sitewise-live-data.png?raw=true)

### Build Agent in Amazon Bedrock
1. Create an S3 bucket and upload the Sample-Wind-Turbine-Maintenance-Guide.docx from the repo and Build Knowledge Base for Amazon Bedrock with the file in S3 bucket as Data Source as mentioned in the AWS documentation here.

2. Download the Lambda functions in the repo and you can deploy with the SAM template associated with the function in same folder or you create the function manually with latest python runtime and uploading the code.

3. Build the Agent in Amazon Bedrock Console as mentioned in the documentation here and create the action groups as per below screen shots, associate the replated Lambda functions to the Actions by mentioning Lambda Function ARNs. The model used is Clude 3 Haiku v1.
![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/agent-config.png?raw=true)

4. Action for Reading Power and Wind Speed of a Wind Turbine by giving Wind Turbine ID and Wind Farm Name as Input Parameters.
![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/action-1-read-power-ws.png?raw=true)

5. Action for Reading other Parameters of a Wind Turbine by giving Wind Turbine ID and Wind Farm Name as Input Parameters.
![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/action-2-read-wtg-measurments.png?raw=true)

6. Action for Summarizing all Wind Farms Data.
![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/action-3-summarize-status.png?raw=true)

7. Action for to find Error condition of Wind Turbines in all Wind Farms Data.
![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/action-4-error-all-wind-farms.png?raw=true)

8. Action to find Error Details of a particular Wind Turbine by giving Wind Turbine ID and Wind Farm Name as Input Parameters.
![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/action-5-error-details-wtg.png?raw=true)

9. Add the Knowledge Base previously created to The Agent for Troubleshooting and Maintenance.
![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/agent-kb-setting.png?raw=true)

10. Once the Agent is built, save and prepare it and you can test the working draft, you can also publish an Alias.

11. Test the Agent with the sample prompts given in the prompts file in repo, below are the testing screen shots.

![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/agent-test-1.png?raw=true)

![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/agent-test-2.png?raw=true)

![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/agent-test-3.png?raw=true)

![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/agent-test-4.png?raw=true)

![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/agent-test-5.png?raw=true)

![alt text](https://github.com/getramki/Integrating-Gen-IA-and-IoT/blob/main/images/agent-test-5.png?raw=true)


In conclusion, the integration of Generative AI and IoT technologies, as demonstrated in this document, offers a promising solution for the wind energy industry. By simulating wind turbine data using Kepware OPC UA Server and IoT Greengrass Core devices, and pushing this data to IoT SiteWise Edge Gateway in the AWS Cloud, the solution addresses the challenges of managing and maintaining wind turbines, especially in remote areas. The development of an intelligent agent with Amazon Bedrock, capable of querying this data, further enhances the efficiency and reliability of wind turbines. This approach not only reduces operational and maintenance costs but also mitigates environmental risks. The detailed implementation steps provided in this document serve as a comprehensive guide for setting up and leveraging this innovative solution.
