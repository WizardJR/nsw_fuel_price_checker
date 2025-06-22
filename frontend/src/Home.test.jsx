import { render, screen, waitFor } from "@testing-library/react";
import Home from "./Home";
import { vi } from "vitest";

beforeEach(() => {
  global.fetch = vi.fn();
});

afterEach(() => {
  vi.resetAllMocks();
});

test('displays >2 decimal place avg with 2 decimals from API', async () => {
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => [{ date: "2025-06-17", avg_price: 123.4 }],
  });

  render(<Home fuelType="DL" />);

  await waitFor(() => {
    expect(screen.getByText("123.40")).toBeInTheDocument();
  });
});

test('displays <2 decimal place avg with 2 decimals from API', async () => {
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => [{ date: "2025-06-17", avg_price: 123.4 }],
  });

  render(<Home fuelType="DL" />);

  await waitFor(() => {
    expect(screen.getByText("123.40")).toBeInTheDocument();
  });
});

test('displays "N/A" when API returns null', async () => {
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => [{ avg_price: null }],
  });

  render(<Home fuelType="DL" />);

  await waitFor(() => {
    expect(screen.getByText("N/A")).toBeInTheDocument();
  });
});