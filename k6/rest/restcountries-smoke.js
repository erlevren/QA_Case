import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 3,
  duration: '5s',
  thresholds: {
    http_req_duration: ['p(95)<1500'],
    http_req_failed: ['rate<0.02'],
  },
};


export default function () {
  const url = 'https://restcountries.com/v3.1/all?fields=name,region';
  const res = http.get(url, {
    headers: {
      'Accept': 'application/json',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) k6-test',
      'Cache-Control': 'no-cache',
    },
    timeout: '10s',
  });

  check(res, {
    'status 200': (r) => r.status === 200,
    'content-type json': (r) => String(r.headers['Content-Type'] || '').includes('application/json'),
  });

  let data;
  try { 
    data = JSON.parse(res.body); 
  } catch { 
    data = null; 
  }

  check(data, {
    'returns array': (d) => Array.isArray(d),
    'has > 100 countries': (d) => Array.isArray(d) && d.length > 100,
  });

  if (Array.isArray(data)) {
    const hasTurkey =
      data.some(c => c?.name?.common === 'Türkiye') ||
      data.some(c => c?.name?.common === 'Turkey');
    check(data, { 
      'contains Turkey/Türkiye': () => hasTurkey 
    });
  }

  sleep(1);
}
