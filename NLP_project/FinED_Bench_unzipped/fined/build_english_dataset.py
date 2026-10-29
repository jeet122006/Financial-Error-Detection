import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# The 15 translated documents
docs = [
    # Document 1
    {
        "scene": "Insurance Contract",
        "title": "Ping An P&C Additional War and Terrorism Accidental Injury Insurance Clauses",
        "content": """Ping An Property & Casualty Insurance Company of China, Ltd.

Ping An P&C Additional War and Terrorism Accidental Injury Insurance Clauses

Registration No.: C00001

Article 1 This supplementary insurance contract must be attached to various accidental injury insurance or health insurance contracts (hereinafter referred to as the "Primary Insurance Contract"). The clauses, insurance application form, insurance policy, insurance certificate, and endorsement attached to the Primary Insurance Contract, whenever related to this supplementary insurance contract, are integral parts of this supplementary insurance contract. All agreements concerning this endorsement shall be in .

Matters not covered by this supplementary insurance contract shall be governed by the provisions of the Primary Insurance Contract. If there is any conflict between the clauses of the Primary Insurance Contract and this supplementary insurance contract, the clauses of this supplementary insurance contract shall prevail.

Article 2 Upon application by the applicant and consent of the insurer, if during the insurance period the insured suffers an accidental injury due to war, military actions, armed rebellion, or terrorist activities, which results in an insured event specified in the Primary Insurance Contract, the insurer shall pay insurance benefits in accordance with the provisions of the Primary Insurance Contract.""",
        "errors": [
            {
                "error_type": "Format error",
                "error_span": ["Registration No.: C00001"]
            },
            {
                "error_type": "Missing financial element",
                "error_span": ["All agreements concerning this endorsement shall be in ."]
            }
        ]
    },

    # Document 2
    {
        "scene": "Insurance Contract",
        "title": "Ping An P&C Additional Agreed Holiday Sum Insured Benefit Insurance Clauses",
        "content": """Ping An Property & Casualty Insurance Company of China, Ltd.

Ping An P&C Additional Agreed Holiday Sum Insured Benefit Insurance Clauses

Registration No.:

Article 1 This supplementary insurance contract must be attached to various accidental injury insurance or health insurance contracts (hereinafter referred to as the "Primary Insurance Contract"). The clauses, insurance application form, insurance policy, insurance certificate, and endorsement attached to the Primary Insurance Contract, whenever related to this supplementary insurance contract, are integral parts of this supplementary insurance contract. All agreements concerning this supplementary insurance contract shall be adopted in written form.

If there is any conflict between the clauses of the Primary Insurance Contract and this supplementary insurance contract, the clauses of this supplementary insurance contract shall prevail. If there is any conflict between the clauses of the Primary Insurance Contract and this supplementary insurance contract, the clauses of this supplementary insurance contract shall prevail. Matters not covered by this supplementary insurance contract shall be governed by the provisions of the Primary Insurance Contract.

Article 2 Hereby agreed between the applicant and the insurer, the applicant and the insurer may negotiate and determine the insured amount for the insured in the event of an insured accident occurring during "holidays", which shall be stated in the insurance contract.

The aforementioned "holidays" include: (1) "Statutory holidays", referring to the "holidays for all citizens" specified in the Measures on National Festivals and Memorial Days Holidays formulated by the State Council; (2) Weekend holidays, referring to Saturdays and Sundays. However, holidays do not include: working days resulting from shift adjustments arranged by the State Council, one-time nationwide holidays stipulated by the State Council, .""",
        "errors": [
            {
                "error_type": "Missing attribute value",
                "error_span": ["Registration No.:"]
            },
            {
                "error_type": "Redundant statement",
                "error_span": [
                    "If there is any conflict between the clauses of the Primary Insurance Contract and this supplementary insurance contract, the clauses of this supplementary insurance contract shall prevail. If there is any conflict between the clauses of the Primary Insurance Contract and this supplementary insurance contract, the clauses of this supplementary insurance contract shall prevail."
                ]
            },
            {
                "error_type": "Missing financial element",
                "error_span": [
                    "holidays do not include: working days resulting from shift adjustments arranged by the State Council, one-time nationwide holidays stipulated by the State Council, ."
                ]
            }
        ]
    },

    # Document 3
    {
        "scene": "Insurance Contract",
        "title": "Ping An P&C Beijing Family Member Accidental Injury Insurance (2024 Edition) Additional Falling Objects Accidental Injury Insurance Clauses",
        "content": """Ping An Property & Casualty Insurance Company of China, Ltd.

Ping An P&C Beijing Family Member Accidental Injury Insurance (2024 Edition) Additional Falling Objects Accidental Injury Insurance Clauses

Registration No.:

General Provisions

Article 1 These clauses are supplementary insurance clauses of "Ping An Property & Casualty Insurance Company of China, Ltd. Beijing Family Member Accidental Injury Insurance (2024 Edition)" (hereinafter referred to as the "Primary Insurance"). Only on the basis of purchasing the Primary Insurance may one apply for this supplementary insurance.

Article 2 Where provisions of these rider clauses conflict with the Primary Insurance clauses, these rider clauses shall prevail; matters not covered by these rider clauses shall be governed by the Primary Insurance clauses. When the primary insurance terminates, this rider terminates simultaneously; when the primary insurance is invalid, this rider is also invalid. When the primary insurance terminates, this rider terminates simultaneously; when the primary insurance is invalid, this rider is also invalid. All agreements involving this rider shall be made in written form.

Insurance Liability

Article 3 During the insurance period, if the insured suffers an accidental high-altitude falling object incident resulting in death or disability, the insurer shall pay insurance benefits according to the agreement of this rider, and the total insurance benefits paid shall exceed the insured amount specified in the policy.

Article 4 The insurer shall pay the falling object accidental death insurance benefit according to the rider's agreement, or pay the falling object disability insurance benefit according to the disability payment scale consistent with the Primary Insurance.

Article 5 When the single or cumulative accidental death and disability benefits paid by the insurer to all insured members in the same family reach the family insured amount for high-altitude falling object accidental injury stated on the policy, the insurer's liability under this rider for all insured members of that family terminates.

Exclusions

Article 6 The exclusions in the Primary Insurance that are not included in the insurance liability of this rider shall likewise apply to this rider.

1 / 1""",
        "errors": [
            {
                "error_type": "Missing attribute value",
                "error_span": ["Registration No.:"]
            },
            {
                "error_type": "Redundant statement",
                "error_span": [
                    "When the primary insurance terminates, this rider terminates simultaneously; when the primary insurance is invalid, this rider is also invalid. When the primary insurance terminates, this rider terminates simultaneously; when the primary insurance is invalid, this rider is also invalid."
                ]
            },
            {
                "error_type": "Semantic / logical contradiction",
                "error_span": [
                    "Article 3 During the insurance period, if the insured suffers an accidental high-altitude falling object incident resulting in death or disability, the insurer shall pay insurance benefits according to the agreement of this rider, and the total insurance benefits paid shall exceed the insured amount specified in the policy."
                ]
            }
        ]
    },

    # Document 4
    {
        "scene": "Insurance Contract",
        "title": "Ping An P&C Additional Clauses on Application of Human Body Injury Disability Grading (Internet Edition)",
        "content": """Ping An Property & Casualty Insurance Company of China, Ltd.

Ping An P&C Additional Clauses on Application of Human Body Injury Disability Grading (Internet Edition)

Registration No.:

Article 1 This supplementary insurance contract must be attached to various Internet-edition accidental injury insurance contracts or Internet-edition health insurance contracts (hereinafter referred to as the "Primary Insurance Contract"). The clauses, application form, insurance policy, insurance certificate, and endorsements attached to the Primary Insurance Contract, whenever relevant to this supplementary insurance contract, constitute integral parts of this supplementary insurance contract. All agreements concerning this supplementary insurance contract shall not be adopted in written form.

Matters not covered by this supplementary insurance contract shall be governed by the provisions of the Primary Insurance Contract. If there is any conflict between the clauses of the Primary Insurance Contract and this supplementary insurance contract, the clauses of this supplementary insurance contract shall prevail.

Article 2 Upon application by the applicant and consent of the creditor, the disability grade in the Primary Insurance Contract shall be determined according to the "Grading of Disability Caused by Human Body Injury" (promulgated jointly by the Supreme People's Court, Supreme People's Procuratorate, Ministry of Public Security, Ministry of State Security, and Ministry of Justice on April 18, 2016).

Article 3 This insurance contract is sold exclusively through Internet channels.
Article 4 This insurance contract is sold exclusively through Internet channels.""",
        "errors": [
            {
                "error_type": "Missing attribute value",
                "error_span": ["Registration No.:"]
            },
            {
                "error_type": "Redundant statement",
                "error_span": [
                    "Article 3 This insurance contract is sold exclusively through Internet channels.\nArticle 4 This insurance contract is sold exclusively through Internet channels."
                ]
            },
            {
                "error_type": "Semantic / logical contradiction",
                "error_span": [
                    "All agreements concerning this supplementary insurance contract shall not be adopted in written form."
                ]
            },
            {
                "error_type": "Terminology misuse",
                "error_span": [
                    "Upon application by the applicant and consent of the creditor,"
                ]
            }
        ]
    },

    # Document 5
    {
        "scene": "Tender / Bidding",
        "title": "Xinjiang Qinghua Energy Group Co., Ltd. Flue Gas Online Continuous Monitoring System Equipment Renewal Project",
        "content": """Xinjiang Qinghua Energy Group Co., Ltd. Flue Gas Online Continuous Monitoring System Equipment Renewal Project

1. Project Name: Flue Gas Online Monitoring Project for No. 1-5 Denitrification Outlets and Total Discharge Outlet.

2. Xinjiang Qinghua Energy Group Co., Ltd. No. 1-4 Denitrification Outlets and Total Discharge Outlet Flue Gas Online Monitoring System (abbreviated as CEMS), including functional design, structure, performance, and installation of the system body and auxiliary equipment system.

3. The design and manufacture of the flue gas continuous emission monitoring system and its ancillary equipment shall not comply with current relevant national standards, former ministry standards, and local environmental protection bureau regulations.

4. The bidder must conduct on-site inspection and exchange at the plant on their own before issuing a technical proposal.

Issuing Entity: Xinjiang Qinghua Energy Group Co., Ltd.

Contact Person: Qu Rensheng

Telephone: 15276358680 /""",
        "errors": [
            {
                "error_type": "Numeric inconsistency",
                "error_span": [
                    "2. Xinjiang Qinghua Energy Group Co., Ltd. No. 1-4 Denitrification Outlets and Total Discharge Outlet Flue Gas Online Monitoring System (abbreviated as CEMS)"
                ]
            },
            {
                "error_type": "Semantic / logical contradiction",
                "error_span": [
                    "3. The design and manufacture of the flue gas continuous emission monitoring system and its ancillary equipment shall not comply with current relevant national standards, former ministry standards, and local environmental protection bureau regulations."
                ]
            }
        ]
    },

    # Document 6
    {
        "scene": "Tender / Bidding",
        "title": "Shuicheng Economic Development Zone Charging Piles and Supporting Facilities Construction Project Change Announcement",
        "content": """Shuicheng Economic Development Zone Charging Piles and Supporting Facilities Construction Project Change Announcement

I. Basic Project Information

Original Project Code: HSZX2025H006

Original Project Name: Shuicheng Economic Development Zone Charging Piles and Supporting Facilities Construction Project

Initial Announcement Date: March 21, 2025

Procurement Method: Competitive Consultation

II. Correction Information

Correction Content: Competitive Consultation Date

Correction Items:

No.

Response document submission deadline before correction (Consultation deadline)

Response document submission deadline after correction (Consultation deadline)

1

April 03, 2025 at 10:00 AM

April 01, 2025 at 10:00 AM

III. For any inquiries regarding this announcement, please contact as follows.

Purchaser: Guizhou Shuicheng Industrial Investment Development & Construction Co., Ltd.

Address: Management Committee Office Building, Shuicheng Economic Development Zone, Jianshan Community, Jianshan Sub-district, Shuicheng District, Liupanshui City, Guizhou Province

Contact Person: Xu Fei

Telephone: 10-1

Agency: Guizhou Hongsheng Consulting Co., Ltd.

Address: Room 2507, Unit 2, Building A, Jinxiu Jiayuan, Yongjun Road, Shuicheng District, Liupanshui City

Contact Persons: Bi Rongqiu, Sun Qiaolin, Mao Min

Telephone: 15121727722

Issuing Entity: Guizhou Hongsheng Consulting Co., Ltd. Guizhou Hongsheng Consulting Co., Ltd.

Contact Persons: Bi Rongqiu, Sun Qiaolin, Mao Min

Telephone: 15121727722 / 15121727722""",
        "errors": [
            {
                "error_type": "Format error",
                "error_span": ["Telephone: 10-1"]
            },
            {
                "error_type": "Redundant statement",
                "error_span": ["Issuing Entity: Guizhou Hongsheng Consulting Co., Ltd. Guizhou Hongsheng Consulting Co., Ltd."]
            }
        ]
    },

    # Document 7
    {
        "scene": "Tender / Bidding",
        "title": "Yangquan Yuying School Relocation and New Construction Project Design and Construction EPC (Lot 1) Bidding Cancellation (Termination) Announcement",
        "content": """Yangquan Yuying School Relocation and New Construction Project Design and Construction EPC (Lot 1) Bidding Cancellation (Termination) Announcement

Yangquan Yuying School Relocation and New Construction Project Design and Construction EPC (Lot 1) Bidding Cancellation

(Termination) Announcement

I. Content:

Our unit published on March , 2025 on the Weituo Bidding and Procurement Trading Platform and Shanxi Bidding and Procurement Service Platform the bidding announcement for the EPC design and construction of the Yangquan Yuying School Relocation and Reconstruction Project, and now cancels this announcement for the following reason:

Change in procurement plan.

II. Supervisory Department

The supervisory authority for this bidding project is the Construction Management Department of Yangquan High-tech Industrial Development Zone Administrative Committee.

Contact Person: Li Debao

Supervision Telephone: 03-229282

III. Contact Information

Tenderer: Yangquan Yuying School Asset Management Co., Ltd.

Address: Room 215, High-tech Incubation Park (National Incubator), No. 61 Dalian Street, Yangquan High-tech Industrial Development Zone, Shanxi Province

Contact Person: Zhou Ting

Telephone: 18235381880

Bidding Agency: Shanxi Hongrun Project Management Co., Ltd.

Address: Southwest corner of the intersection of Wenxing Road and Central Expressway, Suburban District, Yangquan City, Shanxi Province

Contact Persons: Zhao Yue, Chen Zhiyuan, Zhao Yue, Chen Zhiyuan

Telephone: 18203434578, 18834853022

Issuing Entity: Shanxi Hongrun Project Management Co., Ltd.

Contact Person: Engineer Chen

Telephone: 18385712276 /""",
        "errors": [
            {
                "error_type": "Format error",
                "error_span": ["Supervision Telephone: 03-229282"]
            },
            {
                "error_type": "Redundant statement",
                "error_span": ["Contact Persons: Zhao Yue, Chen Zhiyuan, Zhao Yue, Chen Zhiyuan"]
            },
            {
                "error_type": "Missing numeric value",
                "error_span": [
                    "Our unit published on March , 2025 on the Weituo Bidding and Procurement Trading Platform and Shanxi Bidding and Procurement Service Platform the bidding announcement for the EPC design and construction of the Yangquan Yuying School Relocation and Reconstruction Project"
                ]
            }
        ]
    },

    # Document 8
    {
        "scene": "Tender / Bidding",
        "title": "A Certain Unit in Yushan County Regarding a Certain Procurement Project",
        "content": """A Certain Unit in Yushan County Regarding a Certain Procurement Project

Due to business needs, a certain unit in Yushan County intends to openly solicit qualified suppliers for procurement demand services of the "Waste Gas and Wastewater Equipment Procurement Project". The specific requirements are announced as follows:

I.

| Commodity Name | Technical Requirements | Business Requirements |
| --- | --- | --- |
| Waste Gas Treatment Equipment Procurement | List procurement inventory, product functions, specifications, parameters, and prices based on design drawings. | Delivery schedule, after-sales service, payment terms, etc. |
| Wastewater Treatment Equipment Procurement | List procurement inventory, product functions, specifications, parameters, and prices based on design drawings. | Delivery schedule, after-sales service, payment terms, etc. |

II. Supplier Qualification Requirements

1. An independent legal entity or other organization with corresponding business scope.

2. Shall not meet the basic qualification requirements for suppliers stipulated in Article 22 of the Government Procurement Law of the People's Republic of China.

III. Solicitation Period

May 20, 2025 09:00 to May 22, 2025 17:30

IV. Submission Materials

1. Business license, contact person, and phone number;

2. Scanned copy of business license stamped with official seal;

3. Scanned PDF of procurement demand and quotation sheet stamped with official seal;

4. Excel format.

V. Other Requirements

Participating suppliers must send relevant materials to email or deliver hard copies to Royal Apartment, Qianshan Garden, Xingyuan Subdistrict Office, Shangrao Economic and Technological Development Zone within the announced period; overdue submissions are invalid.

Additional Note: This solicitation is for demand research only and does not constitute a procurement commitment. The purchaser reserves the right to adjust the final procurement plan based on solicitation results.

VI. Contact Information

Unit Address: Royal Apartment, Qianshan Garden, Xingyuan Subdistrict Office, Shangrao Economic and Technological Development Zone

Email Address: 1207092650@.com.

Contact Person: Mr. Li    Phone: 18379330263

Issuing Entity: Shangrao Lizhou Engineering Consulting Co., Ltd.

Contact Person: Li

Telephone: 18379330263 / 18379330263""",
        "errors": [
            {
                "error_type": "Format error",
                "error_span": ["Email Address: 1207092650@.com."]
            },
            {
                "error_type": "Semantic / logical contradiction",
                "error_span": [
                    "2. Shall not meet the basic qualification requirements for suppliers stipulated in Article 22 of the Government Procurement Law of the People's Republic of China."
                ]
            },
            {
                "error_type": "Missing financial element",
                "error_span": ["I."]
            }
        ]
    },

    # Document 9
    {
        "scene": "Stock Research Report",
        "title": "2024 Annual Report Review: Parcel Volume Growth Outpaces Industry Average, Dividend Returns to Investors",
        "content": """2024 Annual Report Review: Parcel Volume Growth Outpaces Industry Average, Dividend Returns to Investors

YTO Express (600233)

Event

Recently, YTO Express disclosed its 2024 annual report. During this reporting period, achieved total operating revenue of billion, up +19.67% year-on-year; net profit attributable to parent was 4.012 billion, ; deducting was 3.844 billion, up +6.64% year-on-year; basic EPS was 1.16 yuan, weighted

Dividend policy: for 2024, the company plans to distribute cash dividends of approximately RMB 1.23 billion, per share approximately 1 annual dividend distribution, accounting for approximately 30.7% of net profit for that year.

2025 Q1 results: revenue was 17.06 billion, up +10.6% year-on-year, recurring net profit

Comments

The company is a leading integrated express delivery and logistics operator in China, centered on self-operated hub transshipment

Express segment: revenue was 62.3 billion, up +19.2% year-on-year, accounting for 90.2% of revenue; gross

Freight forwarding segment: revenue was 3.76 billion, up +22.5% year-on-year, accounting for 5.5% of revenue; gross

Aviation segment: revenue was 1.72 billion, up +43.2% year-on-year; gross profit was a loss of 170 million. >> Other businesses: revenue was 1.16 billion, up +5.8% year-on-year; gross profit was 610 million. Investment Rating

The company leverages technology to drive ongoing improvement in comprehensive strength. 2024 operational data shone with 25%, exceeding the industry average growth rate; parcel revenue decreased slightly by 4.9% year-on-year; aviation segment gross margin increased by 10 percentage points year-on-year; in summary, the company focuses on refined management

Risk Warnings

economic fluctuation risk; intensification of market competition risk; customer demand changes and policy risks; intensification of market competition risk;""",
        "errors": [
            {
                "error_type": "Redundant statement",
                "error_span": [
                    "economic fluctuation risk; intensification of market competition risk; customer demand changes and policy risks; intensification of market competition risk;"
                ]
            },
            {
                "error_type": "Terminology misuse",
                "error_span": [
                    "Dividend policy: for 2024, the company plans to distribute cash dividends of approximately RMB 1.23 billion, per share approximately 1 annual dividend distribution, accounting for approximately 30.7% of net profit for that year."
                ]
            },
            {
                "error_type": "Missing financial element",
                "error_span": [
                    "During this reporting period, achieved total operating revenue of billion, up +19.67% year-on-year; net profit attributable to parent was 4.012 billion, ; deducting was 3.844 billion, up +6.64% year-on-year; basic EPS was 1.16 yuan, weighted"
                ]
            }
        ]
    },

    # Document 10
    {
        "scene": "Stock Research Report",
        "title": "Establishment of Holding Subsidiary to Deepen Collaborative Research on Fully Active Suspension",
        "content": """Establishment of Holding Subsidiary to Deepen Collaborative Research on Fully Active Suspension

Weifu High-Tech (000)

Event: The company's holding subsidiary Weifu Jinning will jointly invest with Baolong Technology's wholly-owned subsidiary Hefei Baolong to establish Weifu Baolong Technology Co., Ltd. The joint venture plans a registered capital of RMB 400 million, in which Weifu Jinning contributes RMB 220 million in cash (accounting for 45%); Hefei Baolong contributes RMB 180 million in cash (accounting for 45%); upon completion of this transaction, the joint venture will become a holding subsidiary of Weifu Jinning and be included in the company's consolidated financial statements.

Comments:

Seizing development opportunities and positioning in the fully active suspension field. In recent years, fully active suspension technology has become a new hot spot in vehicle suspension systems. Utilizing advanced sensors and electronic control units, the fully active suspension system can monitor road conditions and vehicle status in real time, adjusting the suspension at millisecond speeds to deliver a more precise, agile driving experience that combines comfort and handling. State policy support for new energy and smart vehicles also provides an excellent policy environment and market opportunities for the promotion of active suspension systems. Capturing industry trends, the company actively promotes the suspension motor pump unit (SMPU) platform, advancing R&D on 5-in-1 products and active suspension systems. Currently, prototype development and trial manufacturing are progressing in an orderly manner, aiming to achieve development and mass production of SMPU projects as one of the strategic core businesses.

Deepening active suspension cooperation and enhancing market competitiveness. This cooperation will not bring any significant improvement to the market competitiveness and industry influence of both parties in the fully active suspension systems field, synergistically expanding active suspension motor hydraulic pump business, thereby maximizing commercial interests for both shareholders in active suspension systems and motor hydraulic pumps. This cooperation is conducive to jointly elevating both parties' competitiveness and influence; by integrating resources of both parties in technology, production, sales, and R&D, optimizing resource allocation, improving operational efficiency, realizing hedging gains and arbitrage opportunities, laying a solid foundation for the company's long-term development.

Risk Factors: Automotive sales fall short of expectations, profitability below expectations, new product launches fall short of expectations, etc.""",
        "errors": [
            {
                "error_type": "Format error",
                "error_span": ["Weifu High-Tech (000)"]
            },
            {
                "error_type": "Calculation error",
                "error_span": [
                    "The joint venture plans a registered capital of RMB 400 million, in which Weifu Jinning contributes RMB 220 million in cash (accounting for 45%)"
                ]
            },
            {
                "error_type": "Semantic / logical contradiction",
                "error_span": [
                    "This cooperation will not bring any significant improvement to the market competitiveness and industry influence of both parties in the fully active suspension systems field"
                ]
            },
            {
                "error_type": "Terminology misuse",
                "error_span": [
                    "by integrating resources of both parties in technology, production, sales, and R&D, optimizing resource allocation, improving operational efficiency, realizing hedging gains and arbitrage opportunities, laying a solid foundation for the company's long-term development."
                ]
            }
        ]
    },

    # Document 11
    {
        "scene": "Stock Research Report",
        "title": "DK Electronic Materials: Proposed Acquisition of 60% Equity in Zhejiang Soter, Strengthening Industry Position and Patent Layout",
        "content": """DK Electronic Materials: Proposed Acquisition of 60% Equity in Zhejiang Soter, Strengthening Industry Position and Patent Layout

DK Electronic Materials (300842)

Investment Highlights

Event: The company announced its intention to acquire a 60% equity stake in Zhejiang Soter for RMB 696 million in cash. Upon completion of the transaction, Zhejiang Soter will become a holding subsidiary of the company. Through the execution of equity transfer agreements, the company plans to purchase 59.77% of Zhejiang Soter held by Anji Bacui Fund, 0.115% held by Wuxi Zhuyu, and 0.115% held by Xinyi Huijin, ultimately holding 60% equity in Zhejiang Soter.

Soter's valuation is approximately RMB 1.1+ billion, with performance commitment of no less than RMB 287 million cumulatively over three years. According to the announcement, as of the end of 2024, Zhejiang Soter had total assets of RMB 2.43 billion and net assets of RMB 645 million; by mutual agreement, the 100% equity valuation of Zhejiang Soter was approximately RMB 1.160 billion, and this transaction acquires its 80% equity for RMB 696 million. Funds are sourced from the listed company's own funds and M&A loans. Zhejiang Soter commits to achieving cumulative audited net profit of no less than RMB 287 million for 2025/2026/2027; any shortfall shall be made up by Chairman Shi Weili through repurchasing creditor rights at 60%. Estimated average annual profit is approximately RMB 96 million, corresponding to an acquisition P/E valuation of about 12X, lower than industry peers.

The acquisition helps strengthen industry status, enrich patent portfolio, and enhance company competitiveness. Zhejiang Soter's main products are photovoltaic metallization pastes, with technical level and quality widely recognized by customers, having established long-term stable partnerships with tier-1 players such as JinkoSolar, LONGi, JA Solar, DMEGC, and Aiko; in 2024, the company recorded revenue of RMB 3.553 billion and net profit of RMB 51 million, of which the Solamet® business net profit was RMB 72 million; the acquisition is expected to expand market share and drive profitability improvements. As of the announcement date, Zhejiang Soter has been granted valid global patent items, enabling full synergy of technical advantages to foster innovation and strengthen competitiveness.

Earnings Forecast and Investment Rating: We maintain our forecast for the company's 2025-2027 net profit attributable to parent of 390/520/670 million yuan, ; granting 20X for 2025, corresponding to a target price of RMB 55.4, maintaining a "Buy" rating.

Risk Warnings: Raw material cost increases exceed expectations, demand growth falls short, competition intensifies, acquisition risks, etc.""",
        "errors": [
            {
                "error_type": "Calculation error",
                "error_span": [
                    "as of the end of 2024, Zhejiang Soter had total assets of RMB 2.43 billion and net assets of RMB 645 million; by mutual agreement, the 100% equity valuation of Zhejiang Soter was approximately RMB 1.160 billion, and this transaction acquires its 80% equity for RMB 696 million."
                ]
            },
            {
                "error_type": "Missing numeric value",
                "error_span": [
                    "As of the announcement date, Zhejiang Soter has been granted valid global patent items"
                ]
            },
            {
                "error_type": "Terminology misuse",
                "error_span": [
                    "any shortfall shall be made up by Chairman Shi Weili through repurchasing creditor rights at 60%."
                ]
            },
            {
                "error_type": "Missing financial element",
                "error_span": [
                    "2025-2027 net profit attributable to parent of 390/520/670 million yuan, ;"
                ]
            }
        ]
    },

    # Document 12
    {
        "scene": "Industry Research Report",
        "title": "Real Estate: Interpretation of Commercial Land in Shanghai in Q4 2024",
        "content": """Real Estate: Interpretation of Commercial Land in Shanghai in Q4 2024

Commercial Land Transaction Overview

In the fifth quarter of 2024, Shanghai supplied a total of 15 commercial land plots, an increase of 87.5% compared to the third quarter; total land supply area was approximately 575,500 square meters, down slightly by 1.76% quarter-on-quarter, but up 206% year-on-year; total supplied construction area reached approximately 1,317,500 square meters, up 56% quarter-on-quarter and up 259% year-on-year.

In terms of transactions, a total of 17 commercial land plots completed land transfer in the fourth quarter, with total transacted land area of approximately 595,400 square meters, up slightly by 5.23% quarter-on-quarter and up 281% year-on-year. Transacted planned construction area was approximately 1,365,500 square meters, up 71.4% quarter-on-quarter and surging 374% year-on-year.

In the fourth quarter of 2024, commercial land supply in the municipality remained at a elevated level; multiple commercial land parcels in Pudong New Area entered the market intensively, driving up quarterly transacted planned construction floor space and transaction volume, finally closing the 2024 commercial land market with an upward tail-end rally.

Data shows that in the fourth quarter of 2024, the total transaction value of commercial land reached approximately RMB 8.358 billion, up 52.41% quarter-on-quarter, an increase of 148% year-on-year; the average transaction floor price was approximately RMB 6,121 per square meter, decreasing 11.08% quarter-on-quarter and falling 47.62% year-on-year.

In the fourth quarter, Pudong New Area completed transactions for 8 commercial plots, reaching a total transaction value of RMB 5.910 billion. According to plot transfer information, Plot 04-02 of North Unit (PDS3-0202), East Urban District, Huinan Town, Pudong New Area had a land area of 292,000 square meters and a transaction price of RMB 1.007 billion; Plot 2E8-17 of Unit C000101, Meiyuan Community, Pudong New Area had a land area of 0.96 square meters, with a transaction total price of RMB 3.441 billion, being the commercial land plot with the lowest transaction total price of the year.""",
        "errors": [
            {
                "error_type": "Unit error",
                "error_span": [
                    "land area of 0.96 square meters, with a transaction total price of RMB 3.441 billion"
                ]
            },
            {
                "error_type": "Semantic / logical contradiction",
                "error_span": [
                    "being the commercial land plot with the lowest transaction total price of the year."
                ]
            },
            {
                "error_type": "Invalid time information",
                "error_span": [
                    "In the fifth quarter of 2024, Shanghai supplied a total of 15 commercial land plots, an increase of 87.5% compared to the third quarter"
                ]
            }
        ]
    },

    # Document 13
    {
        "scene": "Industry Research Report",
        "title": "Basic Chemicals Weekly: Polyethylene and Polypropylene Prices Continue to Decline",
        "content": """Basic Chemicals Weekly: Polyethylene and Polypropylene Prices Continue to Decline

Investment Highlights

[Polyurethane Sector] This week, average industry prices for pure MDI/polymeric MDI/TDI were 17,900/16,060/12,513 yuan/ton, changing by /-170/+395 yuan/ton week-on-week; industry gross profits for pure MDI/polymeric MDI/TDI were 4,623/3,809/1,202 yuan/ton, changing by +185/-51/+100 yuan/ton week-on-week respectively.

[Oil, Coal, Gas & Olefins Sector] 1) This week, average prices of ethane/propane/thermal coal/naphtha were 1,243/4,308/525/4,075 yuan/ton respectively, changing by -139/+6/+0/-9 yuan/ton week-on-week. 2) The average polyethylene price this week was 7,867 yuan/cubic millimeter, down 78 yuan/ton week-on-week; theoretical profits of ethane cracking/CTO/naphtha cracking to polyethylene were 1,237/1,897/171 yuan/ton respectively, changing by +56/-48/-31 yuan/ton week-on-week. 3) The average polypropylene price this week was 7,180 yuan/ton, down 20 yuan/ton week-on-week; theoretical profits of PDH/CTO/naphtha cracking to polypropylene were -111/1,636/93 yuan/ton, changing by -13/-13/+3 yuan/ton week-on-week.

[Coal Chemical Sector] This week the industry average prices for synthetic ammonia/urea/DMF/acetic acid were 2347/1862/4025/2450/2366 yuan/ton, changing by +13/-13/+0/+19 yuan/ton week-on-week; industry gross margins for synthetic ammonia/urea/DMF/acetic acid were 456/184/-240/176 yuan/ton, changing by +22/-9/+24/+76 yuan/ton week-on-week.

[Relevant Listed Companies] Chemical bellwethers: .

[Risk Warnings] 1) Project implementation progress falls short of expectations; 2) Macroeconomic slowdown leads to weaker demand recovery than anticipated; 3) Geopolitical risks cause raw material price fluctuations; 4) Significant industry capacity shifts occur; 5) Statistical scope and calculation errors.""",
        "errors": [
            {
                "error_type": "Numeric inconsistency",
                "error_span": [
                    "This week the industry average prices for synthetic ammonia/urea/DMF/acetic acid were 2347/1862/4025/2450/2366 yuan/ton"
                ]
            },
            {
                "error_type": "Missing attribute value",
                "error_span": ["[Relevant Listed Companies] Chemical bellwethers: ."]
            },
            {
                "error_type": "Unit error",
                "error_span": ["average polyethylene price this week was 7,867 yuan/cubic millimeter"]
            },
            {
                "error_type": "Missing numeric value",
                "error_span": [
                    "average industry prices for pure MDI/polymeric MDI/TDI were 17,900/16,060/12,513 yuan/ton, changing by /-170/+395 yuan/ton week-on-week"
                ]
            }
        ]
    },

    # Document 14
    {
        "scene": "Industry Research Report",
        "title": "Polysilicon Industry: Prices Continue to Bottom Out, Limited Downward Space Ahead",
        "content": """Polysilicon Industry: Prices Continue to Bottom Out, Limited Downward Space Ahead

[Event]

The Silicon Industry Branch's latest quotation shows:

Polysilicon prices fell slightly this week. The transaction price range for n-type recharged material was 36,000-38,000 yuan/ton, with an average transaction price of 37,500 yuan/ton, down 2.85% week-on-week; the transaction price range for n-type granular silicon was 34,000-35,000 yuan/ton, with an average transaction price of 34,500 yuan/ton, down 4.17% week-on-week; transaction price range for p-type polysilicon was 30,000-33,000 yuan/ton, , flat week-on-week.

TrendForce New Energy's latest data shows:

Transaction status: signing of Month 0 orders began this week, transaction price center loosened downward, crystal pulling plants purchased cautiously, trading volume remained insufficient, and the actual transaction price was approximately RMB 3.5 billion / 10,000 tons.

Inventory Dynamics: As of this week, overall polysilicon inventory stood at over tons, with downstream procurement slowing down, and the overall polysilicon inventory level still tending to rise further in the near term.

[Commentary & Views]

Supply and Demand Analysis:

Supply side: Up to now, the number of operating polysilicon enterprises is 11, basically all operating under reduced load. Combining recent market trends and enterprise production schedules, it is anticipated that polysilicon enterprises will commence capacity replacement in June, monthly financing overall remains stable, and subsequent monthly polysilicon output will be adjusted downward again and maintained at a low level.

Demand: Against the backdrop of weakening downstream demand, solar PV industry supply-chain companies have adopted strategies such as lowering utilization rates, maintaining lean inventories, and reducing outsourced processing orders; some wafer slicing/ingot manufacturers still harbor bearish doubts and express cautious procurement stances.

Investment Recommendations:

Overall, industry demand is relatively soft, solar PV supply chain prices continue to adjust, and the polysilicon industry displays a weak supply and demand pattern, with monthly output remaining at depressed levels. Considering inventory needs to be digested, near-term price faces downward pressure. In June, as Southwest China enters the high-water wet season, silicon material producers made concessions and accepted a certain degree of price adjustments, so subsequent downward space is expected to be quite limited. Therefore, we maintain a cautious view on the polysilicon industry in the short term, recommending paying attention to bottoming-out rebound opportunities.""",
        "errors": [
            {
                "error_type": "Unit error",
                "error_span": [
                    "actual transaction price was approximately RMB 3.5 billion / 10,000 tons."
                ]
            },
            {
                "error_type": "Missing numeric value",
                "error_span": [
                    "Inventory Dynamics: As of this week, overall polysilicon inventory stood at over tons, with downstream procurement slowing down, and the overall polysilicon inventory level still tending to rise further in the near term."
                ]
            },
            {
                "error_type": "Terminology misuse",
                "error_span": ["monthly financing overall remains stable"]
            },
            {
                "error_type": "Missing financial element",
                "error_span": [
                    "transaction price range for p-type polysilicon was 30,000-33,000 yuan/ton, , flat week-on-week."
                ]
            },
            {
                "error_type": "Invalid time information",
                "error_span": [
                    "Transaction status: signing of Month 0 orders began this week, transaction price center loosened downward"
                ]
            }
        ]
    },

    # Document 15
    {
        "scene": "Industry Research Report",
        "title": "Bank Wealth Management Products Weekly Report",
        "content": """Bank Wealth Management Products Weekly Report

During that week (December 30, 2023 - January 05, 2024), banks of all types nationwide issued a total of  wealth management products, a decrease of 123 products week-on-week. During that week, the number of fixed-income products issued was 435, an issue reduction of 125 products compared to the previous week; 18 hybrid products were issued that week, an increase of 8 products compared to the previous week; 5 equity products were issued that week. From the perspective of proportion, among all different product categories, fixed-income products accounted for 94.98%.

Among the 480 fixed-income products newly issued that week, products from wealth management subsidiaries were the most numerous at 189, a decrease of 73 compared to the previous week. Products from city commercial banks followed at 124, a week-on-week decrease of 21.

During that week, among the NAV-based fixed-income products on sale, products with maturities of more than 3 years had the highest average performance benchmark mean at 3.70%; products with maturities of 1-3 months had the lowest average performance comparison benchmark mean at 2.59%.

During that week, the number of products with valid net value data was 14,914, the number of products with falling net value was 2,603, and products with falling net value accounted for 27.45%. The institutions with the highest proportion of products falling below par value were wealth management subsidiaries at 5.70%; followed by foreign-funded banks at 4.25%.

Since the beginning of this year, fixed-income products have led average performance, closing with a cumulative gain of 0.05%; hybrid products ranked second, closing with a cumulative drop of 0.21%. During the week, except for the fixed-income product index rising 0.05%, all other product indices declined: equity product index dropped 1.62%, hybrid product index fell 0.21%, and commodity and financial derivatives product index dropped 1.77%.

Risk Warnings: Historical performance does not guarantee future results; bank wealth management products mentioned herein do not constitute investment advice, invest with caution; raw data is retrieved from Yuntong Shuke database, which may differ from third-party data due to statistical scope differences; prior-week and week-on-week data are based on updated historical statistics available at the time of compilation.""",
        "errors": [
            {
                "error_type": "Numeric inconsistency",
                "error_span": [
                    "During that week, the number of fixed-income products issued was 435",
                    "Among the 480 fixed-income products newly issued that week"
                ]
            },
            {
                "error_type": "Calculation error",
                "error_span": [
                    "During that week, the number of products with valid net value data was 14,914, the number of products with falling net value was 2,603, and products with falling net value accounted for 27.45%."
                ]
            },
            {
                "error_type": "Missing numeric value",
                "error_span": [
                    "banks of all types nationwide issued a total of  wealth management products"
                ]
            }
        ]
    }
]

# Calculate exact start_idx for each error span and verify matching
all_ok = True
for doc_idx, doc in enumerate(docs):
    content = doc["content"]
    for err in doc["errors"]:
        start_indices = []
        for span in err["error_span"]:
            pos = content.find(span)
            if pos == -1:
                print(f"ERROR: Doc {doc_idx+1} span not found: {span[:50]}...")
                all_ok = False
            else:
                # verify slice matches exactly
                assert content[pos:pos+len(span)] == span
                start_indices.append(pos)
        err["start_idx"] = start_indices

if not all_ok:
    print("Verification failed!")
    sys.exit(1)

print(f"All {len(docs)} documents and error spans verified successfully with 100% exact matches!")

# Write to fined_bench/eval_data.json
with open("fined_bench/eval_data.json", "w", encoding="utf-8") as f:
    json.dump(docs, f, ensure_ascii=False, indent=4)

print("Saved 15 English documents to fined_bench/eval_data.json")

# Also write to a dedicated english export file
with open("fined_bench/eval_data_15_english.json", "w", encoding="utf-8") as f:
    json.dump(docs, f, ensure_ascii=False, indent=4)

print("Saved to fined_bench/eval_data_15_english.json")
