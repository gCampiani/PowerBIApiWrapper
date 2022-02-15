# PowerBI API Wrapper

This project consists in simplify PowerBI Api usage and retrieve all metadata as a service principal. 

# Pre-requisites

For the connection we need only three information: **client_id**, **client_secret** and **tenant_id** 

**tenant_id** is simple to find but if you are struggling with this point you can read how to [here](https://docs.microsoft.com/en-us/azure/active-directory/fundamentals/active-directory-how-to-find-tenant/).

The tricky part here is how to setup a service principal both in Azure and in PowerBI application, you have many different ways to achieve it here, but the way it worked best for me was following these two tutorials:
>[Enable service principal authentication for read-only admin APIs](https://docs.microsoft.com/en-us/power-bi/admin/read-only-apis-service-principal-authentication)
>
>[Set up metadata scanning in your organization](https://docs.microsoft.com/en-us/power-bi/admin/service-admin-metadata-scanning-setup)

But if you already have a service principal and a PowerBI already configured you can skip this step.

## Setup

We are using Python **3.8.10** . Install the requirements.txt file which contains:
 
 msal **1.16.0**  
requests **2.27.1**



## Examples
The simplest way of authentication:
```python
from powerbi_connector.pbi_connector import PBIApiConnector  
  
  
pbi = PBIApiConnector(client_id='put_your_client_id_here', 
					  client_secret='put_your_client_secret_here', 
					  tenant_id='put_your_tenant_id_here')
```

Get groups as admin using a filter which returns workspaces that are on dedicated capacity:

```python
groups = pbi.get_groups_as_admin(bfilter="type eq 'Workspace' and isOnDedicatedCapacity eq true")
```

Executing a scan to get all metadata from a list of workspaces:

```python
scan = pbi.scan_workspaces(['workspace1', 'workspace2'])  
print("...Starting scan", scan['id'])  
print(scan['status'])  
while scan['status'] != 'Succeeded':  
    scan = pbi.scan_status(scanId=scan['id'])  
    print("...Status", scan['status'])  
result = pbi.scan_result(scanId=scan['id'])
```

Output example from a scan:
```json
{
	"workspaces": [
		{
			"id": "random_uuid4",
			...
			"reports": [...],
			"datasets": [...],
			"dashboards": [...],
			"dataflows": [...]
		}
	],
	"datasourceInstances": [...]
}
```
