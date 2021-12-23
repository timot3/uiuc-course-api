import asyncio
from threading import Lock
from markdownify import markdownify

# key: course name, value: dict that the api would return
course_cache = dict()

mutex = Lock()
fields_to_search = ["name", "label", "description"]


async def __cache_class(course: str, raw: dict, time_length=600) -> None:
    """    
    WARNING: This function should not be called by anything except for another async function.
    https://stackoverflow.com/questions/58774718/asyncio-in-corroutine-runtimeerror-no-running-event-loop
    :param course: the course requested (ie: 'CS 124')
    :param raw: dict of the response that would be returned
    :param time_length: How long to cache for (in seconds). Default 10 min
    :return: None
    """

    if course in course_cache:
        return
    
    mutex.acquire()
    course_cache[course] = raw
    mutex.release()

    await asyncio.sleep(time_length)
    
    mutex.acquire()
    course_cache[course].remove(course)
    mutex.release()

async def cache_classes(courses: dict):
    tasks = []
    for course in courses:
        tasks.append(asyncio.create_task(__cache_class(course['label'], course['raw'])))
    await asyncio.wait(tasks)
        


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d



def descriptions_to_markdown(dict_res):
    for itm in dict_res:
        for field in fields_to_search:
            itm[field] = markdownify(itm[field])

    return dict_res
