import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import Predictions from "./Predictions";

beforeAll(() => {
  global.ResizeObserver = class {
    constructor() {}
    observe() {}
    unobserve() {}
    disconnect() {}
  };
});


const mockData = [
  { date: "2025-06-20", avg_price: 190.56 },
  { date: "2025-06-21", avg_price: 188.74 },
  { date: "2025-06-22", avg_price: 185.93 }
];

beforeEach(() => {
  global.fetch = vi.fn(() =>
    Promise.resolve({
      json: () => Promise.resolve(mockData),
    })
  );
});

afterEach(() => {
  vi.restoreAllMocks();
});

test("renders graph with fetched data", async () => {
  render(<Predictions fuelType="P95" />);
  
  expect(screen.getByText(/Price Range \(P95\)/i)).toBeInTheDocument();
  
  await waitFor(() => {
      expect(screen.getByTestId("predictions-chart-container")).toBeInTheDocument();
  });

});

test("updates graph when interval is changed", async () => {
  render(<Predictions fuelType="P95" />);

  const button = screen.getByRole("button", { name: "30" });
  await userEvent.click(button);

  await waitFor(() => {
    expect(global.fetch).toHaveBeenCalledTimes(4); // 2 for histData, 2 for predData
  });
});