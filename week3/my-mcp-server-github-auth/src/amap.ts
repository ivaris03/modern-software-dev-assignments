import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const AMAP_BASE_URL = "https://restapi.amap.com/v3";
const AMAP_REQUEST_TIMEOUT_MS = 10_000;
const AMAP_MIN_INTERVAL_MS = 200;

let lastAmapRequestTs = 0;

type AmapGeocode = {
	adcode?: string;
	city?: string | string[];
	district?: string;
	level?: string;
	location?: string;
	number?: string;
	province?: string;
	street?: string;
};

type AmapAddressComponent = {
	adcode?: string;
	businessAreas?: Array<{ name?: string }>;
	city?: string | string[];
	citycode?: string;
	district?: string;
	province?: string;
	township?: string;
};

type AmapRegeocode = {
	addressComponent?: AmapAddressComponent;
	formatted_address?: string;
};

type AmapLiveWeather = {
	city?: string;
	humidity?: string;
	province?: string;
	reporttime?: string;
	temperature?: string;
	weather?: string;
	winddirection?: string;
	windpower?: string;
};

type AmapForecastCast = {
	date?: string;
	daypower?: string;
	daytemp?: string;
	dayweather?: string;
	daywind?: string;
	nightpower?: string;
	nighttemp?: string;
	nightweather?: string;
	nightwind?: string;
	week?: string;
};

type AmapForecast = {
	casts?: AmapForecastCast[];
	city?: string;
	province?: string;
	reporttime?: string;
};

type AmapResponse = {
	forecasts?: AmapForecast[];
	geocodes?: AmapGeocode[];
	infocode?: string;
	info?: string;
	lives?: AmapLiveWeather[];
	regeocode?: AmapRegeocode;
	status?: string;
};

function textResult(text: string) {
	return {
		content: [{ text, type: "text" as const }],
	};
}

function normalizeText(value: unknown): string {
	if (Array.isArray(value)) {
		return value.map((item) => normalizeText(item)).filter(Boolean).join(", ");
	}

	if (typeof value === "string") {
		return value;
	}

	if (typeof value === "number" || typeof value === "boolean") {
		return String(value);
	}

	return "";
}

function getAmapApiKey(env: Env): string {
	const apiKey = env.AMAP_API_KEY?.trim();
	if (!apiKey) {
		throw new Error("AMAP_API_KEY is not configured for this Worker.");
	}

	return apiKey;
}

async function sleep(ms: number) {
	await new Promise((resolve) => setTimeout(resolve, ms));
}

async function throttleAmapRequests() {
	const waitMs = lastAmapRequestTs + AMAP_MIN_INTERVAL_MS - Date.now();
	if (waitMs > 0) {
		await sleep(waitMs);
	}
}

async function amapGet(
	env: Env,
	path: string,
	params: Record<string, string>,
): Promise<AmapResponse> {
	await throttleAmapRequests();

	const searchParams = new URLSearchParams();
	for (const [key, value] of Object.entries(params)) {
		searchParams.set(key, value);
	}
	searchParams.set("key", getAmapApiKey(env));
	searchParams.set("output", "JSON");

	const controller = new AbortController();
	const timeoutId = setTimeout(() => controller.abort(), AMAP_REQUEST_TIMEOUT_MS);
	const url = `${AMAP_BASE_URL}${path}?${searchParams.toString()}`;

	console.info("Amap request", { path, params });

	try {
		const response = await fetch(url, {
			method: "GET",
			signal: controller.signal,
		});

		if (!response.ok) {
			throw new Error(`Amap API returned HTTP ${response.status}`);
		}

		const data = (await response.json()) as AmapResponse;
		if (data.status !== "1") {
			const info = normalizeText(data.info) || "unknown error";
			const infocode = normalizeText(data.infocode);
			throw new Error(
				`Amap API error: ${info}${infocode ? ` (code=${infocode})` : ""}`,
			);
		}

		return data;
	} catch (error) {
		if (error instanceof DOMException && error.name === "AbortError") {
			throw new Error("Request to Amap API timed out. Please try again later.");
		}

		throw error;
	} finally {
		clearTimeout(timeoutId);
		lastAmapRequestTs = Date.now();
	}
}

export function registerAmapTools(server: McpServer, env: Env) {
	server.tool(
		"geocode",
		"Convert a Chinese address to geographic coordinates using Amap.",
		{
			address: z
				.string()
				.describe('Structured address string, for example "Beijing Chaoyang District".'),
			city: z
				.string()
				.optional()
				.describe("Optional city name, pinyin, or adcode to narrow the search scope."),
		},
		async ({ address, city }) => {
			if (!address.trim()) {
				return textResult("Error: address parameter is required and cannot be empty.");
			}

			const params: Record<string, string> = { address: address.trim() };
			if (city?.trim()) {
				params.city = city.trim();
			}

			const data = await amapGet(env, "/geocode/geo", params);
			const geocodes = Array.isArray(data.geocodes) ? data.geocodes : [];
			if (!geocodes.length) {
				return textResult(`No geocoding results found for address: ${address}`);
			}

			const lines: string[] = [];
			for (const [index, geocode] of geocodes.entries()) {
				const street = [normalizeText(geocode.street), normalizeText(geocode.number)]
					.filter(Boolean)
					.join(" ");

				lines.push(`Result ${index + 1}:`);
				lines.push(`  Location : ${normalizeText(geocode.location) || "N/A"}`);
				lines.push(`  Province : ${normalizeText(geocode.province)}`);
				lines.push(`  City     : ${normalizeText(geocode.city)}`);
				lines.push(`  District : ${normalizeText(geocode.district)}`);
				lines.push(`  Street   : ${street}`);
				lines.push(`  Adcode   : ${normalizeText(geocode.adcode)}`);
				lines.push(`  Level    : ${normalizeText(geocode.level)}`);
				lines.push("");
			}

			return textResult(lines.join("\n").trim());
		},
	);

	server.tool(
		"reverse_geocode",
		"Convert geographic coordinates to a human-readable address using Amap.",
		{
			longitude: z.number().describe("Longitude value, for example 116.481488."),
			latitude: z.number().describe("Latitude value, for example 39.990464."),
		},
		async ({ longitude, latitude }) => {
			if (longitude < -180 || longitude > 180) {
				return textResult("Error: longitude must be between -180 and 180.");
			}
			if (latitude < -90 || latitude > 90) {
				return textResult("Error: latitude must be between -90 and 90.");
			}

			const location = `${longitude.toFixed(6)},${latitude.toFixed(6)}`;
			const data = await amapGet(env, "/geocode/regeo", {
				extensions: "base",
				location,
			});

			const regeocode = data.regeocode ?? {};
			const component = regeocode.addressComponent ?? {};
			const businessAreas = Array.isArray(component.businessAreas)
				? component.businessAreas
				: [];
			const business = businessAreas
				.map((area) => normalizeText(area?.name))
				.filter(Boolean)
				.join(", ");

			const lines = [
				`Address   : ${normalizeText(regeocode.formatted_address) || "N/A"}`,
				`Province  : ${normalizeText(component.province)}`,
				`City      : ${normalizeText(component.city)}`,
				`District  : ${normalizeText(component.district)}`,
				`Township  : ${normalizeText(component.township)}`,
				`Adcode    : ${normalizeText(component.adcode)}`,
				`City Code : ${normalizeText(component.citycode)}`,
			];

			if (business) {
				lines.push(`Business  : ${business}`);
			}

			return textResult(lines.join("\n"));
		},
	);

	server.tool(
		"get_live_weather",
		"Get current weather conditions for a city adcode using Amap.",
		{
			city_adcode: z
				.string()
				.describe('City administrative code, for example "110000" for Beijing.'),
		},
		async ({ city_adcode }) => {
			if (!city_adcode.trim()) {
				return textResult("Error: city_adcode is required.");
			}

			const data = await amapGet(env, "/weather/weatherInfo", {
				city: city_adcode.trim(),
				extensions: "base",
			});

			const lives = Array.isArray(data.lives) ? data.lives : [];
			if (!lives.length) {
				return textResult(`No live weather data available for adcode: ${city_adcode}`);
			}

			const weather = lives[0];
			return textResult(
				[
					`City        : ${normalizeText(weather.city)} (${normalizeText(weather.province)})`,
					`Weather     : ${normalizeText(weather.weather)}`,
					`Temperature : ${normalizeText(weather.temperature)}degC`,
					`Humidity    : ${normalizeText(weather.humidity)}%`,
					`Wind        : ${normalizeText(weather.winddirection)} ${normalizeText(weather.windpower)} level`,
					`Report Time : ${normalizeText(weather.reporttime)}`,
				].join("\n"),
			);
		},
	);

	server.tool(
		"get_weather_forecast",
		"Get a 4-day weather forecast for a city adcode using Amap.",
		{
			city_adcode: z
				.string()
				.describe('City administrative code, for example "110000" for Beijing.'),
		},
		async ({ city_adcode }) => {
			if (!city_adcode.trim()) {
				return textResult("Error: city_adcode is required.");
			}

			const data = await amapGet(env, "/weather/weatherInfo", {
				city: city_adcode.trim(),
				extensions: "all",
			});

			const forecasts = Array.isArray(data.forecasts) ? data.forecasts : [];
			if (!forecasts.length) {
				return textResult(`No forecast data available for adcode: ${city_adcode}`);
			}

			const forecast = forecasts[0];
			const weekdayMap: Record<string, string> = {
				"1": "Mon",
				"2": "Tue",
				"3": "Wed",
				"4": "Thu",
				"5": "Fri",
				"6": "Sat",
				"7": "Sun",
			};

			const lines = [
				`City: ${normalizeText(forecast.city)} (${normalizeText(forecast.province)})`,
				`Report Time: ${normalizeText(forecast.reporttime)}`,
				"",
			];

			for (const cast of Array.isArray(forecast.casts) ? forecast.casts : []) {
				const weekday = weekdayMap[normalizeText(cast.week)] ?? normalizeText(cast.week);
				lines.push(`  ${normalizeText(cast.date)} (${weekday})`);
				lines.push(
					`    Day   : ${normalizeText(cast.dayweather)}  ${normalizeText(cast.daytemp)}degC  ${normalizeText(cast.daywind)} wind ${normalizeText(cast.daypower)} level`,
				);
				lines.push(
					`    Night : ${normalizeText(cast.nightweather)}  ${normalizeText(cast.nighttemp)}degC  ${normalizeText(cast.nightwind)} wind ${normalizeText(cast.nightpower)} level`,
				);
				lines.push("");
			}

			return textResult(lines.join("\n").trim());
		},
	);
}
