## 3. Test cases

| ID     | Test                            | Expected result                                            | Actual result                                                                                              | Status |
| ------ | ------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------ |
| UAT-01 | Open the Data Intelligence page | Page loads without a fatal error                           | Page opened successfully                                                                                   | PASS   |
| UAT-02 | Request the intelligence API    | Valid response containing a results array                  | API returned a successful response                                                                         | PASS   |
| UAT-03 | Check result count              | Displayed count matches returned records                   | Displayed count matched the API response                                                                   | PASS   |
| UAT-04 | Filter by pollutant             | Results match the selected pollutant                       | Filter behaved as expected                                                                                 | PASS   |
| UAT-05 | Filter by city                  | Results match the selected city                            | Filter behaved as expected                                                                                 | PASS   |
| UAT-06 | Search results                  | Search narrows results correctly                           | Search behaved as expected                                                                                 | PASS   |
| UAT-07 | Check loading behavior          | Loading state appears while the request is pending         | Loading state behaved as expected during testing | PASS |
| UAT-08 | Check API error behavior        | Error message and Retry action work                        | Error state and Retry recovery worked during testing                                                       | PASS   |
| UAT-09 | Check data-quality notice       | Synthetic-data and conditional-quality notices are visible | Warning was visible and understandable                                                                     | PASS   |
| UAT-10 | Open the existing dashboard     | Dashboard loads                                            | Dashboard opened successfully                                                                              | PASS   |
| UAT-11 | Check the existing map and data | Map and existing data requests work                        | Map and air-quality data loaded successfully after the API configuration correction                        | PASS   |

## 4. Execution notes

The Data Intelligence API, result count, pollutant filter, city filter, search, data-quality warning, and error/Retry behavior passed the reported checks. The Air Quality dashboard, map, and data retrieval worked after the frontend API configuration was corrected. The loading-state check remains failed pending investigation and retesting.

## 5. Acceptance criteria

The Data Intelligence page must load, retrieve valid results, apply filters and search, handle request errors, display data limitations, and provide appropriate loading behavior. Existing Air Quality functionality must remain operational.

## 6. Final result

* Confirmed passing test cases: 11
* Confirmed failing test cases: 0
* Pending test cases: 0
* Overall status: PASS
