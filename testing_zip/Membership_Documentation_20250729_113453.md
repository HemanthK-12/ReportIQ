### Power BI Report Documentation

---

#### **Overview**
This Power BI report provides insights into membership data, including totals and member-level details derived from payor-supplied enrollment files. It is designed to support data-driven decision-making by visualizing trends, summaries, and detailed information about contracts, cohorts, and regions. The report is divided into three pages: **Membership Summary**, **Member Detail**, and **Information**.

---

#### **Key Contacts**
- **Report Owner**: ACOE Reporting Team  
- **Contact Email**: [ACOE_VBC@providence.org](mailto:ACOE_VBC@providence.org)  
- **Support Frequency**: Weekly updates on Fridays  

---

#### **Data Flow**
1. **Data Sources**:
   - Snowflake Database (`psjh_prod.west-us-2.azure.snowflakecomputing.com`)
   - Tables: `VBA_MEMBERSHIP_SUMMARY`, `VBA_DATA_SHOP_EMPANELED_PATIENTS`, `Master_Dim`
2. **ETL Process**:
   - Data is extracted from Snowflake using SQL queries.
   - Data transformations include filtering, deduplication, and column derivations.
3. **Power BI Model**:
   - Relationships are established between tables for seamless data exploration.
   - Measures and calculated columns are created for key metrics like `Member Count`, `Date Range`, and `Data Source Display`.

---

#### **Data Explorer**
1. **Membership Summary Page**:
   - Displays membership trends by month and year.
   - Includes slicers for filtering by region, service area, line of business, cohort, and risk contract.
   - Provides grand totals for contract and unique memberships.
2. **Member Detail Page**:
   - Displays member-level details such as name, address, DOB, PCP information, and Epic data.
   - Filters include performance year, region, and service area.
3. **Information Page**:
   - Provides background on the dashboard's purpose and data handling.
   - Explains how the dashboard manages multiple Epic charts and insurance IDs.

---

#### **Dependencies**
The following table dependencies are derived from the relationships in the Power BI model:

| Table                        | Related Tables                       | Relationship Description                                                                 |
|------------------------------|---------------------------------------|-----------------------------------------------------------------------------------------|
| `VBA_MEMBERSHIP_SUMMARY`     | `Master_Dim`                         | Joined via `Key_membership` to `Master_Dim.Key`.                                        |
|                              | `Data Source Display Sort`           | Joined via `Data Source Display`.                                                      |
|                              | `Level of Detail Sort`               | Joined via `Level of Detail`.                                                          |
|                              | `LocalDateTable_*`                   | Multiple date relationships (e.g., `INCURREDYEARMONTH_DT`, `INSERT_DTS`).              |
| `VBA_DATA_SHOP_EMPANELED_PATIENTS` | `Master_Dim`                  | Joined via `Key_empaneled` to `Master_Dim.Key`.                                        |
|                              | `LocalDateTable_*`                   | Multiple date relationships (e.g., `YearMonth`, `DOB`, `INSERT_DTS`).                  |
| `Master_Dim`                 | None                                 | Acts as a dimension table for filtering and grouping data.                             |

---

#### **Data Dictionary**

##### **VBA_MEMBERSHIP_SUMMARY**
| Column Name             | Data Type  | Description                                                                 |
|-------------------------|------------|-----------------------------------------------------------------------------|
| `Region`                | String     | Geographic region of the membership.                                       |
| `Service Area`          | String     | Service area within the region.                                            |
| `Line of Business`      | String     | Line of business associated with the membership.                           |
| `Cohort`                | String     | Cohort classification for the membership.                                  |
| `Risk Contract`         | String     | Risk contract associated with the membership.                              |
| `Member Count`          | Measure    | Total number of members in a given context.                                |
| `Performance Year`      | String     | Year of performance for the membership data.                               |

##### **VBA_DATA_SHOP_EMPANELED_PATIENTS**
| Column Name             | Data Type  | Description                                                                 |
|-------------------------|------------|-----------------------------------------------------------------------------|
| `Payer Member ID`       | String     | Unique identifier for the member provided by the payer.                    |
| `First Name`            | String     | Member's first name.                                                       |
| `Last Name`             | String     | Member's last name.                                                        |
| `DOB`                   | DateTime   | Date of birth of the member.                                               |
| `Region`                | String     | Geographic region of the member.                                           |
| `Service Area`          | String     | Service area within the region.                                            |

##### **Master_Dim**
| Column Name             | Data Type  | Description                                                                 |
|-------------------------|------------|-----------------------------------------------------------------------------|
| `Region`                | String     | Geographic region dimension.                                               |
| `Service Area`          | String     | Service area dimension.                                                    |
| `Line of Business`      | String     | Line of business dimension.                                                |
| `Cohort`                | String     | Cohort dimension.                                                          |

---

#### **Conclusion**
This Power BI report provides a comprehensive view of membership data, enabling users to analyze trends, summaries, and detailed member-level information. The robust data model ensures accurate insights through well-defined relationships and measures. For any issues or enhancements, please contact the ACOE Reporting Team at [ACOE_VBC@providence.org](mailto:ACOE_VBC@providence.org).