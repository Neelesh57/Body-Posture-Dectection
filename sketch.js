async function toggle(type) {
  try {
    const response = await fetch("/toggle", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ [type]: true })
    });
    const result = await response.json();
    console.log("Toggled:", result);
  } catch (err) {
    console.error("Error toggling:", err);
  }
}
