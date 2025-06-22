import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import FuelTypeSelector from "./FuelTypeSelector";
import { vi } from "vitest";

test("renders all fuel type buttons", () => {
  render(<FuelTypeSelector value="DL" onChange={() => {}} />);

  const fuelTypes = ["DL", "E10", "P95", "P98", "U91", "PDL", "LPG"];
  fuelTypes.forEach(ft => {
    expect(screen.getByRole("button", { name: ft })).toBeInTheDocument();
  });
});

test("calls onChange with correct fuel type when clicked", async () => {
  const handleChange = vi.fn();
  render(<FuelTypeSelector value="DL" onChange={handleChange} />);

  const e10Button = screen.getByRole("button", { name: "E10" });
  await userEvent.click(e10Button);

  expect(handleChange).toHaveBeenCalledWith("E10");
});

test("applies 'active' class to the selected fuel type", () => {
  render(<FuelTypeSelector value="E10" onChange={() => {}} />);
  
  const e10Button = screen.getByRole("button", { name: "E10" });
  expect(e10Button.className).toMatch(/active/);
});