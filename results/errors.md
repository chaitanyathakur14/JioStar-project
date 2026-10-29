# Failure examples from results/final_train.json

## right_document_wrong_section (53 queries)

**Q:** Consider the Amendment No. 3 to Wireless Content License Agreement between Fox Mobile Entertainment, Inc. and Glu Mobile Inc.; What is the expiration date of this contract?  
doc_conf=1.0 clause_conf=1.0 abstained=False  
- GOLD `GluMobileInc_20070319_S-1A_EX-10.09_436630_EX-10.09_Content License Agreement4.txt` [598:989]: The rights granted hereunder shall be effective as of the Effective Date and shall expire on December 31, 2006 (the "Term"); provided, however, that with respect to each Property, including Robots, Kingdom of Heaven, Mr. and Mrs. Smith, In Her Shoes, Idiocracy (Oww My Balls) and Ice Age II, all right and licenses granted herein will continue in ful…
- GOT  `SUCAMPOPHARMACEUTICALS,INC_11_04_2015-EX-10.2-STRATEGIC ALLIANCE AGREEMENT.txt` [43486:43977]: made to Acquiror) to be disclosed by applicable Law or any Governmental Authority, (2) generally become available to the public through no fault of the Company, (3) become available to the Company on a non-confidential basis, or (4) are independently…
- GOT  `SUCAMPOPHARMACEUTICALS,INC_11_04_2015-EX-10.2-STRATEGIC ALLIANCE AGREEMENT.txt` [30146:30593]: REPRESENTATIONS AND WARRANTIES Section 3.01 Representations and Warranties of the Company. The Company hereby represents and warrants to Acquiror that, except as disclosed in the Company Disclosure Letter, the statements set forth in Schedule 3.01 ar…
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Service Agreement between BicycleTX Ltd and Nigel Crockett for Chief Business Officer Position; Does this contract include any right of first refusal, right of first offer, or right of first negotiation?  
doc_conf=1.0 clause_conf=0.2976 abstained=False  
- GOLD `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt` [6235:6531]: On or as soon as practicable following the Effective Date, it is intended that you will be granted an option under the Option Plan to acquire 107,417 ordinary shares in the capital of BTL ("Shares") (representing approximately 0.6% of the Company's issued share capital as at the Effective Date).
- GOLD `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt` [6533:7937]: In addition, and conditional on completion of a transaction on terms set out below, you will be granted a second option under the Option Plan, such option being one of: (a) an option to acquire 44,757 Shares (representing approximately 0.25% of the Company's issued share capital as at the Effective Date) granted as soon as practicable following the…
- GOT  `DYNAMEXINC_06_06_1996-EX-10.4-TRANSPORTATION SERVICES AGREEMENT.txt` [16945:17424]: 7.1 A Party shall pay to the other the full amount of any paid claim, loss or damage for which it is liable within forty five (45) days following presentation of supporting documentation. If a Party fails to pay following presentation of supporting d…
- GOT  `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt` [12143:12542]: 9.1 If you are unable to attend at work by reason of sickness or injury or any unauthorised reason you must inform the Company as soon as possible on the first day of absence (and in any event not later than 11.00 am on the first day of absence) and,…
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Cooperation Agreement between HPIL ENERGYTECH Inc. and GINARES GROUP AG for Renewable Energy Projects; What is the expiration date of this contract?  
doc_conf=0.6001 clause_conf=1.0 abstained=False  
- GOLD `HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt` [5604:5739]: The term of this Agreement shall be one (1) year unless terminated earlier in accordance with the terms of this Agreement (the "Term").
- GOT  `HOLIDAYRVSUPERSTORESINC_04_15_2002-EX-10.13-ENDORSEMENT AGREEMENT.txt` [4841:5102]: 3. Term and Termination. A. Unless otherwise provided for in this Agreement, the term of this Agreement shall be three years, commencing on the date of this Agreement and expiring on the third anniversary date of this Agreement (the "Termination
- GOT  `HOLIDAYRVSUPERSTORESINC_04_15_2002-EX-10.13-ENDORSEMENT AGREEMENT.txt` [5108:5490]: Date"). In the event that the Company desires to terminate the Agreement prior to the Termination Date, it shall provide AGI with at least 60 days prior written notice of its intention to terminate this Agreement and this Agreement shall so terminate…
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Cooperation Agreement between HPIL ENERGYTECH Inc. and GINARES GROUP AG for Renewable Energy Projects; Is there a cap on liability under this contract?  
doc_conf=0.6001 clause_conf=0.3584 abstained=False  
- GOLD `HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt` [11380:11583]: GINARES agrees that the sole and exclusive remedy for money damages related to this Agreement and the transactions contemplated hereby shall be the rights to indemnification set forth in this Section 9.
- GOLD `HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt` [12564:12768]: HPIL ET agrees that the sole and exclusive remedy for money damages relating to this Agreement and the transactions contemplated hereby shall be the rights to indemnification set forth in this Section 10.
- GOT  `Loop Industries, Inc. - Marketing Agreement.txt` [13333:13740]: notice, then at a date selected by Joint Venture Company that is within ninety (90) days after Joint Venture Company receives such written notice, the Market and Sale Restriction and the other provisions of this Section 2.7 shall go back into force. …
- GOT  `Loop Industries, Inc. - Marketing Agreement.txt` [14385:14875]: JOINT VENTURE COMPANY SHALL NOT HAVE ANY LIABILITY TO ANY LOOP PARTY WITH RESPECT TO ANY ELIGIBLE CONTRACT THAT DOES NOT BECOME A TRANSFERRED CONTRACT AS PROVIDED IN SECTION 2.3. NOTWITHSTANDING THE FOREGOING, NONE OF THE FOREGOING LIMITATIONS OF LIA…
- DIAGNOSIS: _(write why this failed)_

## wrong_document (19 queries)

**Q:** Consider the Cooperation Agreement between HPIL ENERGYTECH Inc. and GINARES GROUP AG for Renewable Energy Projects; Is there an anti-assignment clause in this contract?  
doc_conf=0.6001 clause_conf=0.3579 abstained=False  
- GOLD `HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt` [17341:17432]: The rights and obligations provided by this Agreement shall not be assignable by any Party.
- GOT  `Loop Industries, Inc. - Marketing Agreement.txt` [29942:30431]: Pursuant to Section 2.4 of the Marketing Agreement, the Assignor desires to assign all rights and obligations under the Loop Sales Contract (the "Transferred Contract") to the Assignee, and the Assignee desires to accept such assignment and assume su…
- GOT  `Loop Industries, Inc. - Marketing Agreement.txt` [10121:10161]: 2.4 Assignment of Transferred Contracts.
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Sponsorship Agreement between R. C. Boyd Enterprises, LLC and Cano Petroleum, Inc. for 'Honey Hole'; What is the expiration date of this contract?  
doc_conf=1.0 clause_conf=1.0 abstained=False  
- GOLD `CANOPETROLEUM,INC_12_13_2007-EX-10.1-Sponsorship Agreement.txt` [3546:3655]: The term of this Agreement shall be one (1) year, commencing January 1, 2008 and ending on December 31, 2008.
- GOT  `ArcGroupInc_20171211_8-K_EX-10.1_10976103_EX-10.1_Sponsorship Agreement.txt` [1322:1818]: The term of this Agreement (the "Term") shall commence as of April 1, 2018 (the "Effective Date") and shall expire upon the later of: (a) the conclusion of the 2022/23 NFL season and (b) the last day in February, 2023 (such expiration date, the "Sche…
- GOT  `VITAMINSHOPPECOMINC_09_13_1999-EX-10.26-SPONSORSHIP AGREEMENT.txt` [34550:34766]: c) All undisputed payments that have accrued prior to the termination or expiration of this Agreement will be payable in full within thirty (30) days thereof.
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Strategic Alliance Agreement between Information System Associates, Inc. and Rubicon Software Group plc; What is the expiration date of this contract?  
doc_conf=1.0 clause_conf=1.0 abstained=False  
- GOLD `DUOSTECHNOLOGIESGROUP,INC_04_21_2009-EX-10.1-STRATEGIC ALLIANCE AGREEMENT.txt` [18727:19214]: Unless terminated sooner, the term of this Agreement shall begin on the Effective Date and continue for three (3) years thereafter (the "Initial Term") and shall automatically renew for additional one (1) year terms on the terms and conditions set forth herein (each a "Renewal Term" and collectively, the "Term") unless either party gives the other …
- GOT  `SUCAMPOPHARMACEUTICALS,INC_11_04_2015-EX-10.2-STRATEGIC ALLIANCE AGREEMENT.txt` [43486:43977]: made to Acquiror) to be disclosed by applicable Law or any Governmental Authority, (2) generally become available to the public through no fault of the Company, (3) become available to the Company on a non-confidential basis, or (4) are independently…
- GOT  `SUCAMPOPHARMACEUTICALS,INC_11_04_2015-EX-10.2-STRATEGIC ALLIANCE AGREEMENT.txt` [30146:30593]: REPRESENTATIONS AND WARRANTIES Section 3.01 Representations and Warranties of the Company. The Company hereby represents and warrants to Acquiror that, except as disclosed in the Company Disclosure Letter, the statements set forth in Schedule 3.01 ar…
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Gas Franchise Agreement between the Town of Vinton and Roanoke Gas Company; What is the expiration date of this contract?  
doc_conf=1.0 clause_conf=1.0 abstained=False  
- GOLD `RgcResourcesInc_20151216_8-K_EX-10.3_9372751_EX-10.3_Franchise Agreement.txt` [1173:1257]: The term of the Franchise shall be twenty (20) years, commencing on January 1, 2016.
- GOT  `PenntexMidstreamPartnersLp_20150416_S-1A_EX-10.4_9042833_EX-10.4_Transportation Agreement.txt` [49724:50217]: Survival. The respective indemnification obligations of the Parties set forth in this Agreement shall survive the expiration of the Term and any termination of this Agreement. [Signature Page Follows] 17 Source: PENNTEX MIDSTREAM PARTNERS, LP, S-1/A,…
- GOT  `PenntexMidstreamPartnersLp_20150416_S-1A_EX-10.4_9042833_EX-10.4_Transportation Agreement.txt` [37799:38209]: This indemnity and defense obligation shall survive the expiration or termination of this Agreement. Transporter shall be responsible for all Taxes or surcharges levied or imposed on it by any Governmental Authority with respect to the Transportation…
- DIAGNOSIS: _(write why this failed)_

## partial_span (11 queries)

**Q:** Consider the Service Agreement between BicycleTX Ltd and Nigel Crockett for Chief Business Officer Position; Are there any exceptions to competitive restrictions in this contract?  
doc_conf=1.0 clause_conf=0.3359 abstained=False  
- GOLD `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt` [33572:34034]: save that nothing in this paragraph 13.2 shall prevent you from holding (with the prior written consent of the Company, which shall not be unreasonably delayed or withheld) up to three percent (3%) of the issued equity share capital of any company where those equity shares are listed on a recognised investment exchange (as defined in section 285 of…
- GOT  `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt` [40601:41098]: beyond what is reasonable in all the circumstances for the protection of the legitimate interests of the Company but would be adjudged reasonable if any particular restriction or restrictions were deleted or if any part or parts of the wording thereo…
- GOT  `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt` [41564:42013]: 14.5 The restrictions contained in paragraph 14.2 above are held by the Company for itself and on trust for any other Group Company and shall be enforceable by the Company on their behalf or by any Group Company (at their request). You shall during t…
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Service Agreement between BicycleTX Ltd and Nigel Crockett for Chief Business Officer Position; How is intellectual property ownership assigned in this contract?  
doc_conf=1.0 clause_conf=0.44 abstained=False  
- GOLD `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt` [44840:45359]: To the extent that such IPRs do not vest automatically in the Company by operation of law, you hereby assign and agree to assign to the Company all of your right, title and interest in any existing and future IPRs which may subsist in any Works for their full term of protection (including any extensions, revivals and renewals) together with the rig…
- GOT  `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt` [48467:48963]: During the term of your employment and at all times thereafter subject always to your obligations to third parties, you shall furnish such information and proper assistance to the Company or any Group Companies as it or they may reasonably require in…
- GOT  `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt` [44547:45041]: 15.3 You will promptly disclose to the Company full details of any Inventions on their creation and provide further details, explanations and demonstrations as the Company from time to time requests. 15.4 All IPRs subsisting in any Works shall be the…
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Strategic Alliance Agreement between Information System Associates, Inc. and Rubicon Software Group plc; Does this contract include an exclusivity agreement?  
doc_conf=1.0 clause_conf=0.3308 abstained=False  
- GOLD `DUOSTECHNOLOGIESGROUP,INC_04_21_2009-EX-10.1-STRATEGIC ALLIANCE AGREEMENT.txt` [5690:6079]: Rubicon hereby grants to ISA during the Term (as defined below) and subject to the exclusions described in 2.4 below an exclusive, non-transferable license in the United States to market, sell, use, display, perform, sublicense and distribute the Rubicon Offerings, the Documentation and, subject to Section 2.2, any upgrades thereto, subject to the …
- GOLD `DUOSTECHNOLOGIESGROUP,INC_04_21_2009-EX-10.1-STRATEGIC ALLIANCE AGREEMENT.txt` [6537:7080]: Rubicon hereby grants to ISA during the Term and subject to the exclusions described in 2.4 below an exclusive, non-transferable license in the United States to grant licenses to use, display, perform and distribute the Rubicon Offerings and the Documentation to other resellers, including, but not limited to, distributors, Original Equipment Manufa…
- GOT  `SUCAMPOPHARMACEUTICALS,INC_11_04_2015-EX-10.2-STRATEGIC ALLIANCE AGREEMENT.txt` [19672:20115]: (c) headings of sections are provided for convenience only and should not affect the construction or interpretation of this Agreement; (d) words importing the masculine gender shall also include the feminine and neutral genders, and vice versa; (e) w…
- GOT  `THERAVANCEBIOPHARMA,INC_05_08_2020-EX-10.2-SERVICE AGREEMENT.txt` [3333:3732]: "Permitted Investment" has the meaning given to it in clause 14.2; and "Termination" means the termination of the Executive's employment under this Agreement however caused, whether lawful or not, and "Termination Date" means the date of Termination.…
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Co-Branding Agreement between PC Quote, Inc. and A.B. Watley, Inc. for Market Data Software; Is there a cap on liability under this contract?  
doc_conf=0.786 clause_conf=0.3584 abstained=False  
- GOLD `PcquoteComInc_19990721_S-1A_EX-10.11_6377149_EX-10.11_Co-Branding Agreement1.txt` [9968:10499]: LIABILITY UNDER THIS AGREEMENT FROM ANY AND ALL CAUSES, INCLUDING, BUT NOT LIMITED TO, PROGRAM MALFUNCTION OR OPERATIONAL NEGLIGENCE, SHALL BE LIMITED TO GENERAL MONEY DAMAGES IN AN AMOUNT NOT TO EXCEED THE TOTAL CHARGES PAID BY ABW FOR THE SERVICES DURING THE MOST RECENT TWELVE (12) MONTHS OF THE AGREEMENT. SUCH LIMITATION SHALL BE THE EXTENT OF P…
- GOLD `PcquoteComInc_19990721_S-1A_EX-10.11_6377149_EX-10.11_Co-Branding Agreement1.txt` [10501:10786]: IN NO EVENT WILL EITHER PARTY BE RESPONSIBLE FOR LOST PROFITS OR SPECIAL INDIRECT, INCIDENTAL OR CONSEQUENTIAL DAMAGES WHICH ABW OR PCQ INCUR OR EXPERIENCE ON ACCOUNT OF ENTERING INTO OR RELYING ON THIS AGREEMENT, EVEN IF PCQ OR ABW HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
- GOT  `PcquoteComInc_19990721_S-1A_EX-10.11_6377149_EX-10.11_Co-Branding Agreement1.txt` [8204:8260]: 6. Limitations of Liability, Remedies On Default A.
- GOT  `PcquoteComInc_19990721_S-1A_EX-10.11_6377149_EX-10.11_Co-Branding Agreement1.txt` [16809:17016]: This Agreement shall not be interpreted or construed to create an association, joint venture or partnership between the parties or to impose any partnership obligation or liability upon either party. B.
- DIAGNOSIS: _(write why this failed)_

## false_abstention (2 queries)

**Q:** Consider the Marketing and Transportation Services Agreement between Purolator Courier Ltd. and Parcelway Courier Systems Canada Ltd. (Dynamex Inc.); Are there any exceptions to competitive restrictions in this contract?  
doc_conf=1.0 clause_conf=0.2724 abstained=True  
- GOLD `DYNAMEXINC_06_06_1996-EX-10.4-TRANSPORTATION SERVICES AGREEMENT.txt` [8102:8548]: It is understood and agreed that Dynamex, from time to time and upon request, may provide pick-up and/or delivery services for other next-day or multiple day courier service providers, as part of their next-day and multiple day service commitment, provided Dynamex' services will not result in the provision of same day service to the customer of the…
- GOLD `DYNAMEXINC_06_06_1996-EX-10.4-TRANSPORTATION SERVICES AGREEMENT.txt` [8558:8856]: Dynamex may continue to provide the same day service it currently provides to Alltours customers, provided revenue to Dynamex from this business does not exceed Five Thousand Dollars ($5,000.00) per month provided there is no change in control, direct or indirect, in Alltours.
- GOT  `PenntexMidstreamPartnersLp_20150416_S-1A_EX-10.4_9042833_EX-10.4_Transportation Agreement.txt` [45671:46164]: Restrictions on Assignment. This Agreement may not be assigned, disposed of, alienated or otherwise transferred by either Party, in whole or in part, without the prior written consent of the other Party, which consent shall not be unreasonably withhe…
- GOT  `DYNAMEXINC_06_06_1996-EX-10.4-TRANSPORTATION SERVICES AGREEMENT.txt` [2304:2496]: v) Any Ministry of Transportation road closure or other acts of government or transport authorities which are beyond the control of the Parties;
- DIAGNOSIS: _(write why this failed)_

**Q:** Consider the Gas Transportation Agreement between PennTex North Louisiana Operating, LLC and MRD Operating LLC; Is there uncapped liability under this contract?  
doc_conf=1.0 clause_conf=0.2615 abstained=True  
- GOLD `PenntexMidstreamPartnersLp_20150416_S-1A_EX-10.4_9042833_EX-10.4_Transportation Agreement.txt` [39668:40153]: NO PARTY SHALL BE LIABLE FOR CONSEQUENTIAL, INCIDENTAL, PUNITIVE, EXEMPLARY OR INDIRECT DAMAGES, LOST PROFITS OR OTHER BUSINESS INTERRUPTION DAMAGES, BY STATUTE, IN TORT OR CONTRACT, OR OTHERWISE; PROVIDED, HOWEVER, THAT THIS LIMITATION SHALL NOT LIMIT A PARTY'S RIGHT TO RECOVERY HEREUNDER FOR ANY SUCH DAMAGES TO THE EXTENT SUCH PARTY IS REQUIRED T…
- GOT  `BONTONSTORESINC_04_20_2018-EX-99.3-AGENCY AGREEMENT.txt` [90144:90639]: Section 12. Insurance. 12.1 Merchant's Liability Insurance. Until the Designation Rights Termination Date or as otherwise directed by Purchaser or set forth in this Agreement, Merchant shall continue to maintain, subject to the Wind-Down Budget and t…
- GOT  `SUCAMPOPHARMACEUTICALS,INC_11_04_2015-EX-10.2-STRATEGIC ALLIANCE AGREEMENT.txt` [7912:8125]: any Hazardous Substance at any location, whether or not owned or operated by the Company or any Subsidiaries, or (b) circumstances forming the basis of noncompliance with or liability under any Environmental Laws.
- DIAGNOSIS: _(write why this failed)_
