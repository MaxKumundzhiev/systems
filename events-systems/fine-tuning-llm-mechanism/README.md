# Description
System should have following API endpoints:
1. POST /answers/upload
-->
    {
        text: random text
    }
<--
    {
        status: 200
    }

This endpoint is a bypass of an LLM work, client will generate n time faked LLM asnwers
API endpoint business logic:
- fetch request
- save request text to db table answers (id, content, created_at)

2. POST /answers/feedback
-->
    {
        answer_id: ...,
        rate: from 0 to 5,
        feedback: random text
    }
<--
{
    status: 200
}
This endpoint should fetch all generated answers from database and generate a fake feedback with rate
and send it to API endpoint.
API endpoint business logic:
- fetch request
- save request data to db table feedbacks (id, answer_id, rate, content, created_at)

At this point we assume there are n answers and n feedbacks for those.
Sort of a snapshot of a system.
