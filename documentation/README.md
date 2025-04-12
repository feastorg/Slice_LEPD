# LED-Photodiode Optical Density Meter

## Parts

- LEDs
  - PD: SFH 213 FA
  - IR: INL-5AMIR15
  - from: https://forum.pioreactor.com/t/od600-or-900-what-is-the-part-number-for-the-ir-led-and-photodiode/375

- Connectors
  - Molex pico blade: https://www.digikey.ca/en/products/detail/molex/0530480210/242864?s=N4IgTCBcDaIKwGYAMAWAHEsBGJIC6AvkA

- LED driver sense resistor
  - https://www.digikey.ca/en/products/detail/stackpole-electronics-inc/RMCF1210FT10R0/1758534
  - 1/2W 1% 1210 (3225 Metric)

## LED Driver

Goal: drive an LED at a set constant current via a PWM signal to produce a consistent light level.

Purpose: we want the LED to emit a set light level with high accuracy (known) and precision (low noise).

### Subcomponents

1. **PWM-to-DAC Filter (Lower Left)**

   - **Input:** A PWM signal enters through an RC network (two resistors and two capacitors) that smooths it into a DC “DAC” voltage.
   - **Outputs:** This DAC voltage is fed to:
     - The noninverting (+) input of the LM339 comparator (top amplifier).
     - The noninverting (+) input of the MCP6242 op amp (bottom amplifier).

2. **LM339 Comparator (Top)**

   - **+ Input:** Receives the filtered DAC voltage.
   - **− Input:** Receives a reference or filtered voltage derived from the +5 V rail.
   - **Output:**
     - Uses an open-collector configuration with a pull-up resistor (1 kΩ) to the +5 V rail.
     - A 200 kΩ resistor from the output back to the DAC input provides hysteresis.
     - The comparator output drives the base of the BC858 PNP transistor through a 10 kΩ resistor.

3. **BC858 PNP Transistor (Top Switch)**

   - **Collector:** Connected directly to the +5 V rail.
   - **Base:** Driven by the LM339 comparator output (via a 10 kΩ resistor).
   - **Emitter:** Connected to the common output node, which is shared with:
     - The drain of the BSS806 N-channel MOSFET.
     - The cathode of the LED (which is further protected by a TVS diode).

4. **MCP6242 Op Amp (Bottom)**

   - **+ Input:** Receives the same DAC voltage from the PWM filter.
   - **− Input:** Connected to the source of the BSS806 MOSFET (the voltage sensed across a 10 Ω resistor).
   - **Output:** Drives the gate of the BSS806 MOSFET (labeled “FET_GATE”) to regulate current.

5. **BSS806 N-Channel MOSFET (Bottom Switch)**

   - **Drain:** Tied to the common output node (also the emitter of the BC858).
   - **Source:** Connects to a 10 Ω resistor that goes to ground. This resistor acts as a current-sense element.
   - **Function:** Controlled by the op amp to regulate the voltage at the source, and hence the current through the LED.

6. **LED and 10 Ω Sense Resistor**

   - **LED Anode:** Connected to the +5 V rail.
   - **LED Cathode:** Connected to the common node (junction of BC858 emitter and MOSFET drain).
   - **Current Path:** +5 V → LED → common node → MOSFET → 10 Ω resistor → Ground.
   - **Sensing:** The voltage across the 10 Ω resistor is used by the op amp for current regulation.

7. **TVS Diode (DF2S6.8M)**
   - **Connection:** Placed between the common output node and ground.
   - **Function:** Provides transient and ESD protection to the circuit.

---

### Function and Theory of Operation

1. **PWM Filtering to Create a DAC:**  
   A low-pass RC filter converts a PWM signal into a stable DC voltage. This voltage represents the desired setpoint for the LED current or voltage.

2. **Op Amp and MOSFET Current Regulation:**

   - The MCP6242 op amp compares the DAC setpoint with the voltage at the MOSFET source (across the 10 Ω sense resistor).
   - Based on this comparison, the op amp adjusts the gate voltage of the BSS806 MOSFET.
   - This regulation maintains the correct current through the LED by ensuring that the sensed voltage (proportional to current) matches the DAC setpoint.

3. **Comparator and PNP Transistor Threshold Control:**

   - The LM339 comparator monitors the DAC voltage against a reference (from the +5 V supply).
   - Through its open-collector output (with hysteresis via the 200 kΩ resistor), it determines if the operating condition is within the desired range.
   - The comparator’s output drives the BC858 PNP transistor, which can provide an alternate current path or act as a switch to either enable or limit the LED current based on threshold conditions.

4. **Combined Regulation and Protection:**
   - **Current Flow:** The LED current flows from the +5 V rail through the LED, into the common node, through the MOSFET, and finally through the 10 Ω resistor to ground.
   - **Protection:** A TVS diode is connected at the output node to guard against voltage spikes.
   - **Feedback:** The op amp continuously adjusts the MOSFET’s gate voltage to ensure that the voltage across the 10 Ω resistor (and thus the LED current) matches the desired value set by the DAC voltage.

**In summary:**  
The circuit converts a PWM signal to a DC level that serves as a setpoint for LED current. The op amp and MOSFET form a linear regulator that adjusts the LED current, while the comparator and PNP transistor provide threshold-based switching or clamping for additional control and protection.

## Photodiode Transimpedance amplifier

Goal: transduce the light level at the photodiode into a steady proportional current and transform this current into a proportional voltage that can be read.

Purpose: read the effective light level

