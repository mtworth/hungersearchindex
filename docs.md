Home
Search Central
Google Trends API (Alpha)
Docs
Was this helpful?

Send feedback
Send requests to the Google Trends API
After you've set everything up, you can send requests to the Google Trends API. The following code samples demonstrate how to send a few requests:

Fetch a geographical breakdown of search interest.
Fetch a time series of search interest.
For a full list of methods, see the reference documentation.

Fetch a geographical breakdown
To fetch a geographical breakdown of search interest, do the following:

Send a fetchGeoBreakdown request.
Get the results of the operation by using the operations.get method.
Send a request to the fetchGeoBreakdown method
To fetch a geographical breakdown of search interest, use the following code.

Python
HTTP request

start_time = datetime(2024, 12, 1)
end_time = datetime(2025, 8, 31)

request = {
    "spec": {
        "expression": {"terms": [{"value": "world cup", "type": "BROAD"}]},
        "geo": {
            "type": "GEO_TYPE_COUNTRY_OR_REGION",
            "code": "GB"
        },
        "timeRange": {
            "startTime": {"seconds": int(start_time.timestamp())},
            "endTime": {"seconds": int(end_time.timestamp())},
        },
        "breakdownResolution": "GEO_TYPE_ADMINISTRATIVE_AREA1",
        "zeroOutNoisyResults": False,
    }
}

fetch_gbd_response = service.v1alpha().fetchGeoBreakdown(body=request).execute()

print(json.dumps(fetch_gbd_response, indent=2))
Here's how the response would look:


{
  "name": "v1alpha.22222222-2222-2222-2222-222222222222",
  "metadata": {
    "@type": "type.googleapis.com/google.trends.searchtrends.v1alpha.GeoBreakdownMetadata",
    "spec": {
      "expression": {
        "terms": [
          {
            "value": "world cup",
            "type": "BROAD"
          }
        ]
      },
      "geo": {
        "code": "GB",
        "type": "GEO_TYPE_COUNTRY_OR_REGION"
      },
      "timeRange": {
        "startTime": "2024-12-01T00:00:00Z",
        "endTime": "2025-08-31T23:59:59Z"
      },
      "breakdownResolution": "GEO_TYPE_ADMINISTRATIVE_AREA1"
    },
    "pointCount": 4
  }
}
Get the results of the geographical breakdown operation
After you send a request to fetch a geographical breakdown, you'll need to get the results by using the operations.get method. The following code gets the results of a geographical breakdown operation that was previously initiated.

Python
HTTP request

operation_name = "operations/" + fetch_gbd_response['name']
fetch_gbd_result = service.operations().get(name=operation_name).execute()

print(json.dumps(fetch_gbd_result, indent=2))
Here's the response for the previous code:


{
  "name": "v1alpha.22222222-2222-2222-2222-222222222222",
  "metadata": {
    "@type": "type.googleapis.com/google.trends.searchtrends.v1alpha.GeoBreakdownMetadata",
    "spec": {
      "expression": {
        "terms": [
          {
            "value": "world cup",
            "type": "BROAD"
          }
        ]
      },
      "geo": {
        "code": "GB",
        "type": "GEO_TYPE_COUNTRY_OR_REGION"
      },
      "timeRange": {
        "startTime": "2024-12-01T00:00:00Z",
        "endTime": "2025-08-31T00:00:00Z"
      },
      "breakdownResolution": "GEO_TYPE_ADMINISTRATIVE_AREA1",
      "zeroOutNoisyResults": false
    },
    "pointCount": 4
  },
  "done": true,
  "response": {
    "@type": "type.googleapis.com/google.trends.searchtrends.v1alpha.FetchGeoBreakdownResponse",
    "geoBreakdown": {
      "points": [
        {
          "subGeo": {
            "code": "GB-ENG",
            "type": "GEO_TYPE_ADMINISTRATIVE_AREA1"
          },
          "searchInterest": 130000,
          "scaledSearchInterest": 100
        },
        {
          "subGeo": {
            "code": "GB-NIR",
            "type": "GEO_TYPE_ADMINISTRATIVE_AREA1"
          },
          "searchInterest": 120000,
          "scaledSearchInterest": 91
        },
        {
          "subGeo": {
            "code": "GB-SCT",
            "type": "GEO_TYPE_ADMINISTRATIVE_AREA1"
          },
          "searchInterest": 110000,
          "scaledSearchInterest": 82
        },
        {
          "subGeo": {
            "code": "GB-WLS",
            "type": "GEO_TYPE_ADMINISTRATIVE_AREA1"
          },
          "searchInterest": 120000,
          "scaledSearchInterest": 89
        }
      ]
    }
  }
}
Fetch a time series
To fetch a time series of search interest, do the following:

Send a request with the fetchTimeSeries method.
Get the results of the operation by using the operations.get method.
Send a request to the fetchTimeSeries method
To fetch a time series of search interest, use the following code.

Python
HTTP request

start_time = datetime(2024, 12, 1)
end_time = datetime(2025, 8, 31)

request = {
    "spec": {
        "expression": {"terms": [{"value": "world cup", "type": "BROAD"}]},
        "geo": {"type": "GEO_TYPE_COUNTRY_OR_REGION", "code": "GB"},
        "timeRange": {
            "startTime": {"seconds": int(start_time.timestamp())},
            "endTime": {"seconds": int(end_time.timestamp())},
        },
        "timeResolution": "MONTH",
    }
}

fetch_ts_operation = service.v1alpha().fetchTimeSeries(body=request).execute()

print(json.dumps(fetch_ts_operation, indent=2))
Here's how the response would look:


{
  "name": "v1alpha.11111111-1111-1111-1111-111111111111",
  "metadata": {
    "@type": "type.googleapis.com/google.trends.searchtrends.v1alpha.TimeSeriesMetadata",
    "spec": {
      "expression": {
        "terms": [
          {
            "value": "world cup",
            "type": "BROAD"
          }
        ]
      },
      "geo": {
        "code": "GB",
        "type": "GEO_TYPE_COUNTRY_OR_REGION"
      },
      "timeRange": {
        "startTime": "2024-12-01T00:00:00Z",
        "endTime": "2025-08-31T23:59:59Z"
      },
      "timeResolution": "MONTH"
    },
    "pointCount": 9
  }
}
Get the results of the time series operation
After you send a request to fetch a time series, you'll need to get the results by using the operations.get method. The following code gets the results of a time series operation that was previously initiated.

Python
HTTP request

operation_name = "operations/" + fetch_ts_operation['name']
print("Getting results for: " + operation_name)

fetch_ts_result = service.operations().get(name=operation_name).execute()

print(json.dumps(fetch_ts_result, indent=2))
Here's how the response would look:


{
  "name": "v1alpha.11111111-1111-1111-1111-111111111111",
  "metadata": {
    "@type": "type.googleapis.com/google.trends.searchtrends.v1alpha.TimeSeriesMetadata",
    "spec": {
      "expression": {
        "terms": [
          {
            "value": "world cup",
            "type": "BROAD"
          }
        ]
      },
      "geo": {
        "code": "GB",
        "type": "GEO_TYPE_COUNTRY_OR_REGION"
      },
      "timeRange": {
        "startTime": "2024-12-01T00:00:00Z",
        "endTime": "2025-08-31T00:00:00Z"
      },
      "timeResolution": "MONTH"
    },
    "pointCount": 9
  },
  "done": true,
  "response": {
    "@type": "type.googleapis.com/google.trends.searchtrends.v1alpha.FetchTimeSeriesResponse",
    "timeSeries": {
      "points": [
        {
          "timeRange": {
            "startTime": "2024-12-01T00:00:00Z",
            "endTime": "2025-01-01T00:00:00Z"
          },
          "searchInterest": 65000,
          "scaledSearchInterest": 17,
          "isPartial": false,
          "extendsPastRequestedTimeRange": false
        },
        {
          "timeRange": {
            "startTime": "2025-01-01T00:00:00Z",
            "endTime": "2025-02-01T00:00:00Z"
          },
          "searchInterest": 43000,
          "scaledSearchInterest": 11,
          "isPartial": false,
          "extendsPastRequestedTimeRange": false
        },
        {
          "timeRange": {
            "startTime": "2025-02-01T00:00:00Z",
            "endTime": "2025-03-01T00:00:00Z"
          },
          "searchInterest": 56000,
          "scaledSearchInterest": 15,
          "isPartial": false,
          "extendsPastRequestedTimeRange": false
        },
        {
          "timeRange": {
            "startTime": "2025-03-01T00:00:00Z",
            "endTime": "2025-04-01T00:00:00Z"
          },
          "searchInterest": 110000,
          "scaledSearchInterest": 29,
          "isPartial": false,
          "extendsPastRequestedTimeRange": false
        },
        {
          "timeRange": {
            "startTime": "2025-04-01T00:00:00Z",
            "endTime": "2025-05-01T00:00:00Z"
          },
          "searchInterest": 48000,
          "scaledSearchInterest": 13,
          "isPartial": false,
          "extendsPastRequestedTimeRange": false
        },
        {
          "timeRange": {
            "startTime": "2025-05-01T00:00:00Z",
            "endTime": "2025-06-01T00:00:00Z"
          },
          "searchInterest": 80000,
          "scaledSearchInterest": 21,
          "isPartial": false,
          "extendsPastRequestedTimeRange": false
        },
        {
          "timeRange": {
            "startTime": "2025-06-01T00:00:00Z",
            "endTime": "2025-07-01T00:00:00Z"
          },
          "searchInterest": 380000,
          "scaledSearchInterest": 100,
          "isPartial": false,
          "extendsPastRequestedTimeRange": false
        },
        {
          "timeRange": {
            "startTime": "2025-07-01T00:00:00Z",
            "endTime": "2025-08-01T00:00:00Z"
          },
          "searchInterest": 230000,
          "scaledSearchInterest": 62,
          "isPartial": false,
          "extendsPastRequestedTimeRange": false
        },
        {
          "timeRange": {
            "startTime": "2025-08-01T00:00:00Z",
            "endTime": "2025-09-01T00:00:00Z"
          },
          "searchInterest": 110000,
          "scaledSearchInterest": 30,
          "isPartial": false,
          "extendsPastRequestedTimeRange": true
        }
      ]
    }
  }
}
science Submit Alpha Tester feedback

Was this helpful?

Send feedback