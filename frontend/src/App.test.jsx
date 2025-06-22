import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./App";
import { vi } from "vitest";

beforeEach(() => {
  global.fetch = vi.fn(() =>
    Promise.resolve({
      json: () => Promise.resolve([{ date: "2025-06-17", avg_price: 123.4 }]),
    })
  );
});

afterEach(() => {
  vi.clearAllMocks();
});

test("renders Home component correctly", async () => {
  render(<App />);
  expect(screen.getByText(/Today's Average Fuel Price/i)).toBeInTheDocument();
  await waitFor(() => expect(screen.getByText(/123.40/)).toBeInTheDocument());
});

test("updates average price when a different fuel type is selected", async () => {
  global.fetch
    .mockResolvedValueOnce({
      ok: true,
      json: async () => [{ avg_price: 100 }],
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => [{ avg_price: 200 }],
    });

  render(<App />);

  await waitFor(() => {
    expect(screen.getByText("100.00")).toBeInTheDocument();
  });

  const e10Button = screen.getByRole("button", { name: "E10" });
  await userEvent.click(e10Button);

  await waitFor(() => {
    expect(screen.getByText("200.00")).toBeInTheDocument();
  });
});