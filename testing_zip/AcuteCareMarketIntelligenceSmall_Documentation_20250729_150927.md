### Power BI Report Documentation

---

## **Overview**
This Power BI report provides insights into market share and out-migration trends for healthcare facilities. It includes visualizations such as pivot tables, slicers, line charts, and maps to analyze data across various dimensions like facilities, patient geography, service lines, and time periods. The report is designed to support decision-making by providing actionable insights into patient movement and market dynamics.

---

## **Key Contacts**
- **Report Owner**: Robin Miller  
  - Email: [robin.miller1@providence.org](mailto:robin.miller1@providence.org)  
  - Subject Line: "Acute Care Market Intelligence Feedback"  
  - Purpose: For reporting issues or providing feedback.
- **Data Engineer**: Not specified. Contact Robin Miller for escalation.

---

## **Data Flow**
1. **Data Sources**:
   - Snowflake Database (`psjh_prod.west-us-2.azure.snowflakecomputing.com`)
   - Tables: `DIM_AGE`, `DIM_CPS`, `DIM_DATE`, `DIM_DIAGNOSIS`, `DIM_FACILITY`, `DIM_MSDRG`, `DIM_PATIENT`, `DIM_PAYOR`, `DIM_PROCEDURE`, `FACT_IP_OP`.

2. **ETL Process**:
   - Data is imported from Snowflake into Power BI using direct queries and transformations.
   - Filters are applied to ensure data relevance (e.g., filtering years between 2021-2025).

3. **Visualization**:
   - Data is visualized using slicers, pivot tables, line charts, and maps.
   - Measures like "Market Share," "Out Migration," and "Cases" are calculated dynamically.

---

## **Data Explorer**
### **Key Visualizations**:
1. **Market Share Section**:
   - Pivot Table: Facility-wise growth and percentage growth.
   - Line Chart: Year-over-year trends in market share.
   - Slicers: Filter by geography, service line, and year.

2. **Out-Migration Section**:
   - Map: Facility-wise out-migration visualization.
   - Pivot Table: Out-migration by service type and year.
   - Area Chart: Trends in out-migration over time.

---

## **Dependencies**
### **Table Relationships**:
The following relationships exist between tables (ER Diagram representation):
1. **FACT_IP_OP**:
   - Linked to `DIM_PATIENT` via `PATIENT_ZIP_CD`.
   - Linked to `DIM_FACILITY` via `FACILITY_KEY`.
   - Linked to `DIM_CPS` via `CPS_KEY`.
   - Linked to `DIM_DATE` via `DATE_KEY`.
   - Linked to `DIM_MSDRG` via `MSDRG_CD`.
   - Linked to `DIM_DIAGNOSIS` via `DIAGNOSIS_CD`.
   - Linked to `DIM_PAYOR` via `PAYOR_KEY`.
   - Linked to `DIM_PROCEDURE` via `HIGHEST_WEIGHTED_CPT_VAL`.

2. **DIM_FACILITY**:
   - Linked to `FACILITY_SYSTEM_NM` via `FACILITY_SYSTEM_NM`.
   - Linked to `FACILITY_NM` via `FACILITY_NM`.

3. **DIM_DATE**:
   - Contains derived columns like `YEAR_NBR`, `QUARTER_OF_YEAR_NBR`, and `YEAR_QTR_DESC`.

---

## **Data Dictionary**
### **Key Tables and Columns**:
1. **FACT_IP_OP**:
   - **DISCHARGE_DTS**: Discharge date (datetime).
   - **ANNUALIZED_ENCOUNTER_CNT**: Annualized encounter count (double).
   - **NON_ANNUALIZED_ENCOUNTER_CNT**: Non-annualized encounter count (double).
   - **Base Class**: Indicates IP/OP classification.

2. **DIM_FACILITY**:
   - **FACILITY_NM**: Facility name (string).
   - **FACILITY_SYSTEM_NM**: System name (string).
   - **FACILITY_LATITUDE_NBR**: Latitude (double).
   - **FACILITY_LONGITUDE_NBR**: Longitude (double).

3. **DIM_PATIENT**:
   - **PATIENT_ZIP_CD**: Patient ZIP code (string).
   - **PATIENT_REGION_NM**: Patient region name (string).
   - **PATIENT_SERVICE_AREA_NM**: Patient service area name (string).

4. **DIM_DATE**:
   - **YEAR_NBR**: Year number (int64).
   - **QUARTER_OF_YEAR_NBR**: Quarter number (double).
   - **YEAR_QTR_DESC**: Year-quarter description (string).

5. **DIM_CPS**:
   - **CPS Institute**: CPS institute name (string).
   - **CPS Program**: CPS program name (string).

6. **Measures**:
   - **Cases**: Total cases based on encounter counts.
   - **Market Share System/Facility**: Market share percentage for systems or facilities.
   - **New Out Migration**: Count of patients migrating out of the system.

---

## Conclusion
This Power BI report is a comprehensive tool for analyzing healthcare market share and patient migration trends. It integrates data from multiple dimensions and provides actionable insights through interactive visualizations. For further assistance or feedback, contact Robin Miller at the provided email address.