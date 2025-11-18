import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import NearbyStations from "./NearbyStations";
import { vi } from "vitest";

beforeEach(() => {
  global.fetch = vi.fn();
});

afterEach(() => {
  vi.resetAllMocks();
});

test("displays loading while fetching stations", async () => {
  global.fetch.mockImplementation(() => new Promise(() => {}));
  render(<NearbyStations fuelType="P95" />);
  
  expect(screen.getByText("Loading…")).toBeInTheDocument();
});

test("displays stations from API", async () => {
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => [
      {
        name: "7-Eleven Burwood",
        address: "Cnr Parramatta & Shaftsbury Rds, Burwood NSW 2134",
        postcode: "2134",
        latitude: -33.869406,
        longitude: 151.108603,
        fuel_type: "P95",
        price: 180.0,
        pricetimestamp: 1762923963
      }
    ],
  });
  
  render(<NearbyStations fuelType="DL" />);
  
  await waitFor(() => {
    expect(screen.getByText("7-Eleven Burwood")).toBeInTheDocument();
    expect(screen.getByText("Cnr Parramatta & Shaftsbury Rds, Burwood NSW 2134")).toBeInTheDocument();
    expect(screen.getByText("180.0")).toBeInTheDocument();
  });
});

test("displays N/A if no data", async () => {
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => [
      {}
    ],
  });
  
  render(<NearbyStations fuelType="P95" />);
  
  await waitFor(() => {
    expect(screen.getByText("N/A")).toBeInTheDocument();
  });
});

test("displays error message if API returns HTTP 400", async () => {
  global.fetch.mockResolvedValueOnce({
    ok: false,
    status: 400,
    statusText: "Bad Request",
  });

  render(<NearbyStations fuelType="DL" />);

  await waitFor(() => {
    expect(screen.getByText("Failed to load stations")).toBeInTheDocument();
  });
});

test("displays error message if API returns HTTP 404", async () => {
  global.fetch.mockResolvedValueOnce({
    ok: false,
    status: 404,
    statusText: "Not Found",
  });

  render(<NearbyStations fuelType="DL" />);

  await waitFor(() => {
    expect(screen.getByText("Failed to load stations")).toBeInTheDocument();
  });
});

test("updates postcode input and triggers fetch on search button click", async () => {
  global.fetch.mockResolvedValue({
    ok: true,
    json: async () => [],
  });

  render(<NearbyStations fuelType="P95" />);

  const input = screen.getByPlaceholderText("Enter postcode");
  const button = screen.getByText("Search");

  fireEvent.change(input, { target: { value: "2000" } });
  expect(input.value).toBe("2000");

  fireEvent.click(button);

  await waitFor(() => {
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("postcode=2000")
    );
  });
});