# uiuc-course-api
REST API with course description searching. This api is designed specifically for the [UIUC Classes Bot on Discord](https://github.com/timot3/uiuc-classes-bot), but is live for anyone to use.

# Endpoints

## Classes


### GET /api/classes/?subject=val&?number=val

Returns the classes matching the provided `subject` and `number` parameters.
Both of these parameters are optional; for example, a GET to `/api/classes/?subject=CS` will return all stored CS courses.

Example response (`?subject=CS&number=124`):
```
[
    {
        "credit_hours": "3 hours.",
        "degree_attributes": "Quantitative Reasoning I course.",
        "description": "Basic concepts in computing and fundamental techniques for solving computational problems. Intended as a first course for computer science majors and others with a deep interest in computing. Credit is not given for both CS 124 and CS 125. Prerequisite: Three years of high school mathematics or MATH 112.",
        "gpa": "None",
        "label": "CS 124",
        "name": "Introduction to Computer Science I",
        "number": 124,
        "subject": "CS",
        "yearterm": "Spring 2022"
    }
]
```

### GET /api/classes/all/

Returns the all stored courses.

Example response:
```
[
    {
        "credit_hours": "3 hours.",
        "degree_attributes": "Social & Beh Sci - Soc Sci, and Cultural Studies - US Minority course.",
        "description": "Interdisciplinary introduction to the basic concepts and approaches in Asian American Studies. Surveys the various dimensions of Asian American experiences including history, social organization, literature, arts, and politics.",
        "gpa": "3.59",
        "label": "AAS 100",
        "name": "Intro Asian American Studies",
        "number": 100,
        "subject": "AAS",
        "yearterm": "Spring 2022"
    },
    {
        "credit_hours": "3 hours.",
        "degree_attributes": "Cultural Studies - US Minority course.",
        "description": "Interdisciplinary introduction to the basic concepts and approaches in Arab American Studies. Addresses the issues of history, race, social organization, politics, literature, and art related to Arab American experiences.",
        "gpa": "3.76",
        "label": "AAS 105",
        "name": "Introduction to Arab American Studies",
        "number": 105,
        "subject": "AAS",
        "yearterm": "Spring 2022"
    },
    {
        "credit_hours": "3 hours.",
        "degree_attributes": "Social & Beh Sci - Soc Sci, and Cultural Studies - US Minority course.",
        "description": "Same as AFRO 201, LLS 201, and PS 201. See PS 201.",
        "gpa": "None",
        "label": "AAS 201",
        "name": "US Racial & Ethnic Politics",
        "number": 201,
        "subject": "AAS",
        "yearterm": "Spring 2022"
    },
    ...
]
```


## Search

### GET /api/classes/search/?query=val

Uses the [Whoosh](https://whoosh.readthedocs.io/en/latest/) library to perform a search on the `name`, `label`, 
and `description` fields of the database based on the provided query. Returns the relevant found text markdownified.
Also returns the original entry under the `raw` field.
Example response (`?query=digital+signal+processing`):
```
[
    {
        "credit_hours": "3 hours.",
        "description": "and discrete-time **signal** **processing** with an emphasis...analog-to-**digital** and **digital**-to-analog conversion...and applications of **digital** **signal** **processing**. Prerequisite",
        "gpa": "3.02",
        "label": "ECE 310",
        "name": "**Digital** **Signal** **Processing**",
        "number": 310,
        "raw": {
            "credit_hours": "3 hours.",
            "description": "Introduction to discrete-time systems and discrete-time signal processing with an emphasis on causal systems; discrete-time linear systems, difference equations, z-transforms, discrete convolution, stability, discrete-time Fourier transforms, analog-to-digital and digital-to-analog conversion, digital filter design, discrete Fourier transforms, fast Fourier transforms, spectral analysis, and applications of digital signal processing. Prerequisite: ECE 210.",
            "gpa": "3.02",
            "label": "ECE 310",
            "name": "Digital Signal Processing",
            "number": 310,
            "subject": "ECE",
            "yearterm": "Spring 2022"
        },
        "subject": "ECE",
        "yearterm": "Spring 2022"
    },
    {
        "credit_hours": "4 hours.",
        "description": "concept review of **digital** **signals** and systems; computer...aided **digital** filter design, quantization...to adaptive **signal** **processing**. Prerequisite",
        "gpa": "3.66",
        "label": "ECE 551",
        "name": "**Digital** **Signal** **Processing** II",
        "number": 551,
        "raw": {
            "credit_hours": "4 hours.",
            "description": "Basic concept review of digital signals and systems; computer-aided digital filter design, quantization effects, decimation and interpolation, and fast algorithms for convolution and the DFT; introduction to adaptive signal processing. Prerequisite: ECE 310 and ECE 313.",
            "gpa": "3.66",
            "label": "ECE 551",
            "name": "Digital Signal Processing II",
            "number": 551,
            "subject": "ECE",
            "yearterm": "Fall 2021"
        },
        "subject": "ECE",
        "yearterm": "Fall 2021"
    },
    ...
]
```
