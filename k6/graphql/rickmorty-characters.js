import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 2,
  duration: '10s',
  thresholds: {
    'http_req_duration{req:positive}': ['p(95)<1500'],
    'http_req_failed{req:positive}': ['rate<0.08'],
  },
};

export default function () {
  const url = 'https://rickandmortyapi.com/graphql';
  const query = `
    query ($page: Int!) {
      characters(page: $page) {
        results { id name species status }
      }
    }
  `;
  const variables = { page: 1 };

  // POSITIVE
  const res = http.post(url, JSON.stringify({ query, variables }), {
    headers: { 'Content-Type': 'application/json' },
    tags: { req: 'positive' },
  });

  check(res, {
    'status 200': (r) => r.status === 200,
    'json response': (r) => String(r.headers['Content-Type'] || '').includes('application/json'),
  });

  let body;
  try { 
    body = JSON.parse(res.body); 
  } catch { 
    body = null; 
  }

  check(body, {
    'has data.characters.results': (b) => Array.isArray(b?.data?.characters?.results),
    'at least 1 character': (b) => (b?.data?.characters?.results || []).length > 0,
  });

  if (Array.isArray(body?.data?.characters?.results)) {
    const names = body.data.characters.results.map(x => x.name);
    check(body, { 
      'includes Rick Sanchez': () => names.includes('Rick Sanchez')
     });
  }

  // NEGATIVE
  const bad = http.post(url, JSON.stringify({ query: 'query { nopeField }' }), {
    headers: { 'Content-Type': 'application/json' },
    tags: { req: 'negative' },
  });

  check(bad, {
    'invalid query handled': (r) => {
      if (r.status === 400) 
        return true;
      try {
        const body = JSON.parse(r.body);
        return r.status === 200 && body.errors;
      } catch {
        return false;
      }
    },
  });

  sleep(1);
}
