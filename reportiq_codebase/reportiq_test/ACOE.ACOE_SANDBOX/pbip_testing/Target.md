<a id="top"></a>
<h1>Membership Summary</h1>

[[_TOC_]]

# Overview
The Membership Summary dashboard is designed to provide membership data from payor enrollment files and Risk Arrangement Data (RAD) sources.

[Top](#Top)


# Key Contacts
Business: [Harry Wolberg](mailto:harry.wolberg@providence.org);
Data Explorer: [Kristin Bigback](mailto:kristin.bigback@providence.org);
Database Development: [Kristin Bigback](mailto:kristin.bigback@providence.org);


# Data Explorer
[Membership Summary](https://app.powerbi.com/groups/ce6d9dc5-a845-4245-9ee7-098310ae1e32/reports/157aaf34-1fcc-4757-b465-f6948d0c7f1c/ReportSection?experience=power-bi) is a PowerBI native tool for end-users to self-service and explore membership data.

[Top](#Top)


# Data Flow
![Membership Data Flow.png](/.attachments/Membership%20Data%20Flow-2e3bbc01-4346-4818-a90c-b017c8a6cda1.png)


# Entity Relationship Diagram
![Membership ERD.png](/.attachments/Membership%20ERD-7b2ebba8-355b-4d95-9a4e-46943ecadeb6.png)


# Data Dictionary
[Data Dictionary](https://app.powerbi.com/groups/ce6d9dc5-a845-4245-9ee7-098310ae1e32/reports/ca308167-43a6-41ce-b918-0ff167bdf74c/ReportSection98269606130c2b219b5b?experience=power-bi)


# Deployment Guide
Create Tables and Insert Views (containing SQL logic to load tables).
Run the Insert View to load the table.  

[Top](#Top)


# Dependencies
1. DMS_VBC.FACT_VBA_MEMBERSHIP_SUMMARY
   	- DMS_VBC.FACT_MEMBER_ENROLLMENT
	- POPULATION_HEALTH.SHARED.RAD_PERFORMANCEMONTH
	- DMS_VBC.DIM_RAD_CONTRACT
	- DMS_VBC.VW_RAD_LOB
	- DMS_VBC.VW_RAD_APM_FRAMEWORK
2. RPT_VBC.VBA_MEMBERSHIP_SUMMARY
	- DMS_VBC.FACT_VBA_MEMBERSHIP_SUMMARY

[Top](#Top)


# ETL/Control M Schedule 
**Control M Folder name**: 
- ACOE_DATAMARTS_DAILY_VBC (FACT_VBA_MEMBERSHIP_SUMMARY) 
- ACOE_DATAMARTS_WEEKLY_FRI_VBC (VBA_MEMBERSHIP_SUMMARY)

**Calendar Frequency:** 
- Daily (FACT_VBA_MEMBERSHIP_SUMMARY) 
- Weekly on Fridays (VBA_MEMBERSHIP_SUMMARY)

**Mart Dependencies:** POPULATION_HEALTH Tables (FACT_VBA_MEMBERSHIP_SUMMARY) 

**Start Time:** 
- 7:30 AM (FACT_VBA_MEMBERSHIP_SUMMARY) 
- 9:00 AM (VBA_MEMBERSHIP_SUMMARY)

**Control-M Notifications:**
* **Job Failure email notification:** [Kristin Bigback](mailto:Kristin.Bigback@providence.org), [Harry Wolberg](mailto:Harry.Wolberg@providence.org), [Yvette Yutzie](mailto:Yvette.Yutzie@providence.org)
* **Job Success email notification:** [Kristin Bigback](mailto:Kristin.Bigback@providence.org)

| Sequence | Job | Dependency | Environment |
|----------|-----|------------|--------|
|1 |UTILITY.USP_LOAD_TABLE_FROM_VIEW('DMS_VBC.VW_INSERT_FACT_VBA_MEMBERSHIP_SUMMARY', 'DMS_VBC.FACT_VBA_MEMBERSHIP_SUMMARY', 'F');| | CDW|
|2 |UTILITY.USP_LOAD_TABLE_FROM_VIEW('RPT_VBC.VW_INSERT_VBA_MEMBERSHIP_SUMMARY', 'RPT_VBC.VBA_MEMBERSHIP_SUMMARY', 'F');| 1 | CDW |

[Top](#Top)