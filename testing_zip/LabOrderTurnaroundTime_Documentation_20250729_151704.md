# Power BI Report Documentation

## Overview
This document provides a comprehensive overview of the Power BI report, detailing its structure, data flow, dependencies, and key components. The report focuses on lab result turnaround times across various locations, procedures, and time periods. It includes visualizations for median and mean turnaround times, comparisons to system benchmarks, and trends over time.

---

## Key Contacts
- **Report Owner:** Analytics Center of Excellence (ACOE)
- **Contact for Feedback:** [ACOE Feedback Form](https://providence4.sharepoint.com/sites/AnalyticsCenterofExcellenceACOE/SitePages/Feedback-for-the-ACOE.aspx?csf=1&web=1&e=yssr6V)

---

## Data Flow
1. **Data Source:** The report pulls data from the Snowflake database (`psjh_prod.west-us-2.azure.snowflakecomputing.com`), specifically the `LAB_ORDER_TURNAROUND` table in the `RPT_LAB` schema.
2. **Data Transformation:** Data is processed using Power Query transformations to clean and prepare it for analysis.
3. **Data Model:** The data is modeled with relationships between the main table (`VW_LAB_ORDER_TURNAROUND`) and date tables (`LocalDateTable_*`) for time-based analysis.
4. **Visualizations:** The report includes bar charts, line charts, slicers, and tooltips to provide insights into lab turnaround times.

---

## Data Explorer
### Key Visualizations:
1. **Lab Turnaround Median Time by Location:**
   - Displays median turnaround times by state, hospital, and procedure.
   - Includes comparisons to system-wide medians.
2. **Lab Turnaround Mean Time by Location:**
   - Similar to the median visualization but focuses on mean turnaround times.
3. **Trends Over Time:**
   - Line charts showing 24-week trends for turnaround times.
4. **Day of Week Analysis:**
   - Clustered column charts analyzing turnaround times by weekdays.

### Filters:
- **State(s):** Dropdown slicer for filtering by state.
- **Hospital:** Dropdown slicer for filtering by hospital.
- **Procedure:** Dropdown slicer for filtering by procedure.
- **Date Range:** Relative date slicer for selecting time periods.

---

## Dependencies (ER Diagram Representation)
### Tables and Relationships:
1. **VW_LAB_ORDER_TURNAROUND (Main Table):**
   - Columns: `PROC_NAME`, `ORDER_ID`, `RESULT_DATE`, `RCV_TO_RSLT`, `RESULT_DT`, `CREATE_TS`, etc.
   - Measures: `System Median`, `System Mean`, `color`, `color mean`.
   - Relationships:
     - `RESULT_DATE` → `LocalDateTable_2f9ad19d.Date`
     - `RESULT_DT` → `LocalDateTable_13609593.Date`
     - `CREATE_TS` → `LocalDateTable_1d0705c1.Date`

2. **LocalDateTable_* (Date Tables):**
   - Columns: `Date`, `Year`, `MonthNo`, `Month`, `QuarterNo`, `Quarter`, `Day`.
   - Hierarchies: `Date Hierarchy` (Year > Quarter > Month > Day).

3. **Perspective (Parameter Table):**
   - Columns: `Location`, `Parameter Fields`, `Parameter Order`.

---

## Data Dictionary
### VW_LAB_ORDER_TURNAROUND
| Column Name         | Data Type | Description                                                                 |
|---------------------|-----------|-----------------------------------------------------------------------------|
| PROC_NAME           | String    | Name of the procedure.                                                     |
| ORDER_ID            | Double    | Unique identifier for lab orders.                                          |
| RESULT_DATE         | DateTime  | Date when the result was finalized.                                         |
| RCV_TO_RSLT         | Double    | Time in minutes from receiving to resulting.                               |
| RESULT_DT           | DateTime  | Date when the result was recorded.                                         |
| CREATE_TS           | DateTime  | Timestamp when the record was created.                                     |
| States              | String    | Derived column categorizing service areas into states.                     |
| WeekDayName         | String    | Day of the week derived from RESULT_DATE.                                  |
| WeekID              | Integer   | Week number derived from RESULT_DT.                                        |

### LocalDateTable_*
| Column Name         | Data Type | Description                                                                 |
|---------------------|-----------|-----------------------------------------------------------------------------|
| Date                | DateTime  | Calendar date.                                                             |
| Year                | Integer   | Year extracted from the date.                                              |
| MonthNo             | Integer   | Month number (1-12).                                                       |
| Month               | String    | Full month name (e.g., January).                                           |
| QuarterNo           | Integer   | Quarter number (1-4).                                                      |
| Quarter             | String    | Quarter label (e.g., Qtr 1).                                               |
| Day                 | Integer   | Day of the month (1-31).                                                   |

### Perspective
| Column Name         | Data Type | Description                                                                 |
|---------------------|-----------|-----------------------------------------------------------------------------|
| Location            | String    | Parameterized location field for filtering visuals.                        |
| Parameter Fields    | String    | Internal field for parameter metadata.                                     |
| Parameter Order     | Integer   | Order of parameters for sorting purposes.                                  |

---

## Conclusion
This Power BI report provides actionable insights into lab turnaround times, enabling stakeholders to identify bottlenecks and improve efficiency. The data model is robust, leveraging Snowflake as the primary data source and integrating time intelligence features for dynamic analysis. For further assistance or feedback, contact the ACOE team using the provided link.