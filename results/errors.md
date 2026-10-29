# Failure examples from results/final_train.json

## false_abstention (73 queries)

**Q:** Consider the Service Agreement between BicycleTX Ltd and Nigel Crockett for Chief Business Officer Position; What is the governing law for this contract?  
doc_conf=1.0 clause_conf=0.0 abstained=True  
- GOLD `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt` [53956:54252]: This Agreement shall be governed by and interpreted in accordance with the laws of England and Wales and the parties to this Agreement submit to the exclusive jurisdiction of the Courts of England and Wales in relation to any claim, dispute or matter arising out of or relating to this Agreement.
- GOT  `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt` [0:500]: Exhibit 10.11 DATED 26 September 2019 BicycleTX Ltd and Nigel Crockett ___________________________________________________ SERVICE AGREEMENT ___________________________________________________ THIS AGREEMENT is made on 26 September 2019 BETWEEN: (1) …
- GOT  `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt` [56500:57000]: any other way, including but not limited to by way of a merger. 19 THIS AGREEMENT has been executed and delivered as a deed by or on behalf of the parties on the date written at the top of page 1. Executed as a Deed by BICYCLETX LIMITED acting by a d…
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Cooperation Agreement between HPIL ENERGYTECH Inc. and GINARES GROUP AG for Renewable Energy Projects; What is the governing law for this contract?  
doc_conf=0.566 clause_conf=0.0 abstained=True  
- GOLD `HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt` [16867:17117]: This Agreement and its application and interpretation will be governed exclusively by its terms and the laws of the State of Nevada (USA), and excluding any conflicts of law provisions which would require the application of any law other than Nevada.
- GOT  `HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt` [3500:4000]: T THIS COOPERATION AGREEMENT ("Agreement") is signed this 5th day of January, 2015 (the "Closing Date"), by and between HPIL ENERGYTECH Inc., a Nevada (USA) corporation (hereafter "HPIL ET") and GINARES GROUP AG, a private company domiciled in Switze…
- GOT  `HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt` [0:500]: COOPERATION AGREEMENT made by and between HPIL ENERGYTECH Inc. and GINARES GROUP AG January 5, 2015 Table of Contents 1. Term.............................................................................................................................…
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Cooperation Agreement between HPIL ENERGYTECH Inc. and GINARES GROUP AG for Renewable Energy Projects; Is there an anti-assignment clause in this contract?  
doc_conf=0.566 clause_conf=0.0 abstained=True  
- GOLD `HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt` [17341:17432]: The rights and obligations provided by this Agreement shall not be assignable by any Party.
- GOT  `HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt` [3500:4000]: T THIS COOPERATION AGREEMENT ("Agreement") is signed this 5th day of January, 2015 (the "Closing Date"), by and between HPIL ENERGYTECH Inc., a Nevada (USA) corporation (hereafter "HPIL ET") and GINARES GROUP AG, a private company domiciled in Switze…
- GOT  `HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt` [0:500]: COOPERATION AGREEMENT made by and between HPIL ENERGYTECH Inc. and GINARES GROUP AG January 5, 2015 Table of Contents 1. Term.............................................................................................................................…
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Cooperation Agreement between HPIL ENERGYTECH Inc. and GINARES GROUP AG for Renewable Energy Projects; Is there a cap on liability under this contract?  
doc_conf=0.566 clause_conf=0.0 abstained=True  
- GOLD `HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt` [11380:11583]: GINARES agrees that the sole and exclusive remedy for money damages related to this Agreement and the transactions contemplated hereby shall be the rights to indemnification set forth in this Section 9.
- GOLD `HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt` [12564:12768]: HPIL ET agrees that the sole and exclusive remedy for money damages relating to this Agreement and the transactions contemplated hereby shall be the rights to indemnification set forth in this Section 10.
- GOT  `HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt` [3500:4000]: T THIS COOPERATION AGREEMENT ("Agreement") is signed this 5th day of January, 2015 (the "Closing Date"), by and between HPIL ENERGYTECH Inc., a Nevada (USA) corporation (hereafter "HPIL ET") and GINARES GROUP AG, a private company domiciled in Switze…
- GOT  `HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt` [0:500]: COOPERATION AGREEMENT made by and between HPIL ENERGYTECH Inc. and GINARES GROUP AG January 5, 2015 Table of Contents 1. Term.............................................................................................................................…
- DIAGNOSIS: _(write why this failed)_

## right_document_wrong_section (45 queries)

**Q:** Consider the Amendment No. 3 to Wireless Content License Agreement between Fox Mobile Entertainment, Inc. and Glu Mobile Inc.; What is the expiration date of this contract?  
doc_conf=1.0 clause_conf=0.3232 abstained=False  
- GOLD `GluMobileInc_20070319_S-1A_EX-10.09_436630_EX-10.09_Content License Agreement4.txt` [598:989]: The rights granted hereunder shall be effective as of the Effective Date and shall expire on December 31, 2006 (the "Term"); provided, however, that with respect to each Property, including Robots, Kingdom of Heaven, Mr. and Mrs. Smith, In Her Shoes, Idiocracy (Oww My Balls) and Ice Age II, all right and licenses granted herein will continue in ful…
- GOT  `GluMobileInc_20070319_S-1A_EX-10.09_436630_EX-10.09_Content License Agreement4.txt` [0:500]: AMENDMENT NO. 3 Dated as of February 19, 2007 Reference is hereby made to that certain fully executed Wireless Content License Agreement Number 12965 dated as of December 16, 2004, as amended November 11, 2005 and March 27, 2006 (the "Agreement"), be…
- GOT  `GluMobileInc_20070319_S-1A_EX-10.09_436630_EX-10.09_Content License Agreement4.txt` [1500:1902]: e to all of the terms and conditions hereof. Glu Mobile Inc. ("Licensee") Fox Mobile Entertainment, Inc. ("Fox") By: /s/ Albert A. Pimentel By: /s/ Jamie Samson Name: Albert A. Pimentel Name: Jamie Samson Its: EVP and CFO Its: Senior Vice President D…
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Service Agreement between BicycleTX Ltd and Nigel Crockett for Chief Business Officer Position; Are there any exceptions to competitive restrictions in this contract?  
doc_conf=1.0 clause_conf=0.6065 abstained=False  
- GOLD `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt` [33572:34034]: save that nothing in this paragraph 13.2 shall prevent you from holding (with the prior written consent of the Company, which shall not be unreasonably delayed or withheld) up to three percent (3%) of the issued equity share capital of any company where those equity shares are listed on a recognised investment exchange (as defined in section 285 of…
- GOT  `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt` [0:500]: Exhibit 10.11 DATED 26 September 2019 BicycleTX Ltd and Nigel Crockett ___________________________________________________ SERVICE AGREEMENT ___________________________________________________ THIS AGREEMENT is made on 26 September 2019 BETWEEN: (1) …
- GOT  `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt` [56500:57000]: any other way, including but not limited to by way of a merger. 19 THIS AGREEMENT has been executed and delivered as a deed by or on behalf of the parties on the date written at the top of page 1. Executed as a Deed by BICYCLETX LIMITED acting by a d…
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Service Agreement between BicycleTX Ltd and Nigel Crockett for Chief Business Officer Position; Does this contract include any right of first refusal, right of first offer, or right of first negotiation?  
doc_conf=1.0 clause_conf=0.642 abstained=False  
- GOLD `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt` [6235:6531]: On or as soon as practicable following the Effective Date, it is intended that you will be granted an option under the Option Plan to acquire 107,417 ordinary shares in the capital of BTL ("Shares") (representing approximately 0.6% of the Company's issued share capital as at the Effective Date).
- GOLD `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt` [6533:7937]: In addition, and conditional on completion of a transaction on terms set out below, you will be granted a second option under the Option Plan, such option being one of: (a) an option to acquire 44,757 Shares (representing approximately 0.25% of the Company's issued share capital as at the Effective Date) granted as soon as practicable following the…
- GOT  `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt` [0:500]: Exhibit 10.11 DATED 26 September 2019 BicycleTX Ltd and Nigel Crockett ___________________________________________________ SERVICE AGREEMENT ___________________________________________________ THIS AGREEMENT is made on 26 September 2019 BETWEEN: (1) …
- GOT  `IGENEBIOTECHNOLOGYINC_05_13_2003-EX-1-JOINT VENTURE AGREEMENT.txt` [39501:40000]: the date Igene receives such notice. 11.3. In the event of a contradiction between the terms of this Article 11 and any Support Services Agreement, the terms of the Support Services Agreement shall govern. 12. RIGHT OF FIRST REFUSAL; TERMINATION OF T…
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Service Agreement between BicycleTX Ltd and Nigel Crockett for Chief Business Officer Position; How is intellectual property ownership assigned in this contract?  
doc_conf=1.0 clause_conf=0.7086 abstained=False  
- GOLD `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt` [44840:45359]: To the extent that such IPRs do not vest automatically in the Company by operation of law, you hereby assign and agree to assign to the Company all of your right, title and interest in any existing and future IPRs which may subsist in any Works for their full term of protection (including any extensions, revivals and renewals) together with the rig…
- GOT  `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt` [0:500]: Exhibit 10.11 DATED 26 September 2019 BicycleTX Ltd and Nigel Crockett ___________________________________________________ SERVICE AGREEMENT ___________________________________________________ THIS AGREEMENT is made on 26 September 2019 BETWEEN: (1) …
- GOT  `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt` [56500:57000]: any other way, including but not limited to by way of a merger. 19 THIS AGREEMENT has been executed and delivered as a deed by or on behalf of the parties on the date written at the top of page 1. Executed as a Deed by BICYCLETX LIMITED acting by a d…
- DIAGNOSIS: _(write why this failed)_

## partial_span (12 queries)

**Q:** Consider the Strategic Alliance Agreement between Information System Associates, Inc. and Rubicon Software Group plc; Are the licenses granted under this contract non-transferable?  
doc_conf=1.0 clause_conf=0.7743 abstained=False  
- GOLD `DUOSTECHNOLOGIESGROUP,INC_04_21_2009-EX-10.1-STRATEGIC ALLIANCE AGREEMENT.txt` [5690:6080]: Rubicon hereby grants to ISA during the Term (as defined below) and subject to the exclusions described in 2.4 below an exclusive, non-transferable license in the United States to market, sell, use, display, perform, sublicense and distribute the Rubicon Offerings, the Documentation and, subject to Section 2.2, any upgrades thereto, subject to the …
- GOLD `DUOSTECHNOLOGIESGROUP,INC_04_21_2009-EX-10.1-STRATEGIC ALLIANCE AGREEMENT.txt` [6537:7080]: Rubicon hereby grants to ISA during the Term and subject to the exclusions described in 2.4 below an exclusive, non-transferable license in the United States to grant licenses to use, display, perform and distribute the Rubicon Offerings and the Documentation to other resellers, including, but not limited to, distributors, Original Equipment Manufa…
- GOT  `DUOSTECHNOLOGIESGROUP,INC_04_21_2009-EX-10.1-STRATEGIC ALLIANCE AGREEMENT.txt` [0:500]: Exhibit 10.1 STRATEGIC ALLIANCE AGREEMENT This Strategic Alliance Agreement (this "Agreement"), effective as of 15 April, 2009 (the "Effective Date"), is by and between Information System Associates, Inc., a Florida Corporation whose registered offic…
- GOT  `DUOSTECHNOLOGIESGROUP,INC_04_21_2009-EX-10.1-STRATEGIC ALLIANCE AGREEMENT.txt` [46000:46298]: zed representatives have executed this Agreement as of the date first written above. Information Systems Associates, Inc. Rubicon Software Group plc By: /s/ Joseph P. Coschera By /s/ Alistair C. Hancock: Name: Joseph P. Coschera Name: Alistair C. Han…
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Supply Agreement between Florida Chemical Company, LLC and Flotek Chemistry, LLC for Terpene Products; Does this contract include any volume restrictions?  
doc_conf=1.0 clause_conf=0.2531 abstained=False  
- GOLD `FLOTEKINDUSTRIESINCCN_05_09_2019-EX-10.1-SUPPLY AGREEMENT.txt` [958:1076]: "Maximum Quantity" means [***] pounds of Terpene Product per Year, prorated for any partial Year included in the Term.
- GOLD `FLOTEKINDUSTRIESINCCN_05_09_2019-EX-10.1-SUPPLY AGREEMENT.txt` [3210:3809]: FCC shall be obligated to accept all such purchase orders unless the amount ordered for a Year exceeds the Maximum Quantity, or orders for a particular quarter exceed [***] pounds or exceed the Flotek forecast for that quarter by more than 25%, provided, however, that, in such event, FCC shall communicate Flotek of the time period that will be requ…
- GOT  `FLOTEKINDUSTRIESINCCN_05_09_2019-EX-10.1-SUPPLY AGREEMENT.txt` [0:500]: Exhibit 10.1 Information identified with "[***]" has been excluded from this exhibit because it is both not material and would likely cause competitive harm to the registrant if publicly disclosed. SUPPLY AGREEMENT This Supply Agreement (the "Agreeme…
- GOT  `FLOTEKINDUSTRIESINCCN_05_09_2019-EX-10.1-SUPPLY AGREEMENT.txt` [19001:19355]: have executed this Agreement as of the date and year first set forth above. FLORIDA CHEMICAL COMPANY, LLC: By: /s/ Elizabeth T. Wilkinson Name: Elizabeth T. Wilkinson Title: Chief Financial Officer FLOTEK CHEMISTRY, LLC: By: /s/ Elizabeth T. Wilkinso…
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Marketing and Transportation Services Agreement between Purolator Courier Ltd. and Parcelway Courier Systems Canada Ltd. (Dynamex Inc.); Is there a clause preventing the solicitation of customers in this contract?  
doc_conf=1.0 clause_conf=0.199 abstained=False  
- GOLD `DYNAMEXINC_06_06_1996-EX-10.4-TRANSPORTATION SERVICES AGREEMENT.txt` [7291:7515]: Except for the joint marketing efforts referred to in Section 3.1 (v) above, Purolator agrees not to directly or indirectly solicit next day or multiple day freight from existing sameday customers of Dynamex.
- GOLD `DYNAMEXINC_06_06_1996-EX-10.4-TRANSPORTATION SERVICES AGREEMENT.txt` [7537:7727]: Except for the joint marketing efforts referred to in Section 3.1 (v) above, Dynamex agrees not to directly or indirectly solicit overnight freight from customers of Purolator.
- GOT  `DYNAMEXINC_06_06_1996-EX-10.4-TRANSPORTATION SERVICES AGREEMENT.txt` [0:500]: 1 EXHIBIT 10.4 MARKETING AND TRANSPORTATION SERVICES AGREEMENT THIS AGREEMENT made in duplicate this 20 day of November, 1995. B E T W E E N: PUROLATOR COURIER LTD. ("Purolator") - and - PARCELWAY COURIER SYSTEMS CANADA LTD
- GOT  `DYNAMEXINC_06_06_1996-EX-10.4-TRANSPORTATION SERVICES AGREEMENT.txt` [48500:49000]: e written by their proper officers duly authorized on that behalf. PARCELWAY COURIER SYSTEMS CANADA LTD. Per: (ILLEGIBLE) 11/20/95 c/s ----------------------------- Per: c/s ----------------------------- PUROLATOR COURIER LTD. Per: (ILLEGIBL
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Endorsement Agreement between ABG-Shaq, LLC and Papa John's International, Inc.; Are there any exceptions to competitive restrictions in this contract?  
doc_conf=1.0 clause_conf=0.322 abstained=False  
- GOLD `PapaJohnsInternationalInc_20190617_8-K_EX-10.1_11707365_EX-10.1_Endorsement Agreement.txt` [4441:5829]: Subject to the terms contained herein, PAPA JOHN'S and ABG agree and acknowledge that during the Term of this Agreement and for one (1) year thereafter, ABG shall be prohibited from granting any rights for CELEBRITY identical or similar to the rights granted to PAPA JOHN'S hereunder to any entity other than PAPA JOHN'S for the purpose of directly p…
- GOT  `PapaJohnsInternationalInc_20190617_8-K_EX-10.1_11707365_EX-10.1_Endorsement Agreement.txt` [0:500]: Exhibit 10.1 ENDORSEMENT AGREEMENT THIS ENDORSEMENT AGREEMENT ("Agreement") is made and entered into effective March 15, 2019 (the "Effective Date") by and among, on the one hand, ABG-Shaq, LLC, a Delaware limited liability company ("ABG") for the pe…
- GOT  `PapaJohnsInternationalInc_20190617_8-K_EX-10.1_11707365_EX-10.1_Endorsement Agreement.txt` [13001:13500]: to include PAPA JOHN'S, Celebrity's Endorsement of PAPA JOHN'S Products, and the existence of a partnership between ABG and PAPA JOHN'S in connection with CELEBRITY in Press Releases, subject to PAPA JOHN'S approval, such approval not to be unreasona…
- DIAGNOSIS: _(write why this failed)_

## false_answer (11 queries)

**Q:** Consider the Co-Production Agreement between Bluefin Studios LLC and Marigold Films Limited; Who owns the intellectual property in derivative works?  
doc_conf=0.1823 clause_conf=0.7343 abstained=False  
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Music Synchronization License between Harborline Records and Quillmark Television; What territories are covered by the license?  
doc_conf=0.1543 clause_conf=0.2123 abstained=False  
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Format License Agreement between Tangerine Formats BV and Lumen Broadcasting Corp.; What is the license fee per episode?  
doc_conf=0.0874 clause_conf=0.5553 abstained=False  
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Clip License Agreement between Meridian Newsreel Archive and Fablehouse Digital; May clips be used for promotional trailers?  
doc_conf=0.1205 clause_conf=0.3095 abstained=False  
- DIAGNOSIS: _(write why this failed)_
