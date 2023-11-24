import http from "k6/http";
import { sleep } from "k6";

const getRandom = (list) => {
  return list[Math.floor(Math.random() * list.length)];
};

//const BASE_URL = "https://kommuneinfo.dev.skip.statkart.no";
const BASE_URL = "http://127.0.0.1:5000";

const tests = [
  {
    name: "/punkt test 1",
    url: "/punkt?nord=6584369.41252981&ost=263532.118296728&koordsys=25833",
  },
  {
    name: "/punkt test 2",
    url: "/punkt?nord=59.33167164389&ost=10.842312662935&koordsys=4258",
  },
  {
    name: "/fylker test",
    url: "/fylker",
  },
  {
    name: "/fylker/{fylkesnummer} test",
    url: "/fylker/03",
  },
  {
    name: "/fylker/{fylkesnummer}/omrade test",
    url: "/fylker/03/omrade",
  },
  {
    name: "/kommuner test",
    url: "/kommuner",
  },
  {
    name: "/kommuner/illustrasjonskart test",
    url: "/kommuner/illustrasjonskart",
  },
  {
    name: "/kommuner/{kommunenummer} test",
    url: "/kommuner/3107",
  },
  {
    name: "/kommuner/{kommunenummer}/nabokommuner test",
    url: "/kommuner/3107/nabokommuner",
  },
  {
    name: "/kommuner/{kommunenummer}/omrade test",
    url: "/kommuner/3107/omrade",
  },
  {
    name: "/sok test",
    url: "/sok?knavn=fredrikstad",
  },
  {
    name: "/fylkerkommuner test",
    url: "/fylkerkommuner",
  },
  {
    name: "/fylkerkommuner annen utkoord test",
    url: "/fylkerkommuner?utkoordsys=25833",
  },
];

export default function () {
  let randomTest = getRandom(tests);
  http.get(`${BASE_URL}${randomTest.url}`);
}
