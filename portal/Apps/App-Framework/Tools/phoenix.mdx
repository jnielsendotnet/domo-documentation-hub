# Domo Phoenix

Build beautiful charts using Phoenix, Domo's powerful charting engine for Domo Apps.

## Documentation

You can find this library on [npm](https://www.npmjs.com/package/@domoinc/domo-phoenix).

This README provides a quick overview of how to use Phoenix. For more detailed information, please see the [official documentation](https://domoapps.github.io/domo-phoenix/).

If you are looking to build a Domo Dev Studio app that can query data from Domo and visualize it with Phoenix, please refer to the official [Starter Kit](https://github.com/DomoApps/StarterKit).

## Installation

The Phoenix library is available on npm: [@domoinc/domo-phoenix on npm](https://www.npmjs.com/package/@domoinc/domo-phoenix).

```sh
npm install @domoinc/domo-phoenix
```

## Usage

Import and use the library in your project:

```javascript
import { Chart, CHART_TYPE, DATA_TYPE, MAPPING } from '@domoinc/domo-phoenix';

const data = {
  // This is the data you get back from the Domo Data API
  rows: [
    ['Low', 'Corporate', 8582.8875],
    ['High', 'Home Office', 14415.941],
    ['Low', 'Consumer', 1264.8215],
    ['Medium', 'Small Business', 21478.799],
    ['Critical', 'Consumer', 2621.97],
    ['Not Specified', 'Consumer', 2211.31],
    ['Critical', 'Corporate', 10087.1315],
    ['Not Specified', 'Corporate', 4407.138],
    ['High', 'Consumer', 11667.366],
    ['High', 'Corporate', 19503.323],
    ['Low', 'Small Business', 1735.3715],
    ['Low', 'Home Office', 10057.42],
    ['Medium', 'Home Office', 7691.02],
    ['Critical', 'Small Business', 4036.064],
    ['Not Specified', 'Small Business', 84.99],
    ['High', 'Small Business', 689.74],
    ['Critical', 'Home Office', 7416.828],
    ['Not Specified', 'Home Office', 1839.26],
    ['Medium', 'Consumer', 4280.034],
    ['Medium', 'Corporate', 7965.238],
  ],
  // You provide the names, types, and mappings for your columns, in order
  columns: [
    {
      type: DATA_TYPE.STRING,
      name: 'Order Priority',
      mapping: MAPPING.SERIES,
    },
    {
      type: DATA_TYPE.STRING,
      name: 'Customer Segment',
      mapping: MAPPING.ITEM,
    },
    {
      type: DATA_TYPE.DOUBLE,
      name: 'Sales',
      mapping: MAPPING.VALUE,
    },
  ],
};

// Chart options
const options = {
  width: 600,
  height: 500,
};

// Create the Phoenix chart
const chart = new Chart(CHART_TYPE.BAR, data, options);

// Append the chart's canvas element to your app
document.getElementById('myDiv').appendChild(chart.canvas);

// Render the chart when you're ready for the user to see it
chart.render();
```

## Configuration

### Chart Options

The following options are customizable, along with their default values:

| Property | Description                                                                         | Type             | Default |
| -------- | ----------------------------------------------------------------------------------- | ---------------- | ------- |
| width    | The width of the Phoenix Chart                                                      | number           | `500`   |
| height   | The height of the Phoenix Chart                                                     | number           | `400`   |
| animate  | Whether or not the chart should animate in when being drawn                         | boolean          | `true`  |
| colors   | An array of hex codes to use in drawing charts. Overrides the default color palette | Array of strings | `null`  |

### Chart Types

An enum, `CHART_TYPE`, is provided with all supported chart types. Here are a few examples of common chart types:

- `BAR`
- `STACKEDBAR`
- `HORIZ_BAR`
- `LINE`
- `CURVED_LINE`
- `STACKED_AREA`
- `NAUTILUS`
- `PIE`
- `FUNNEL`
- `BUBBLE`
- `DONUT`
- `WORD_CLOUD`

### Data Types

An enum, `DATA_TYPE`, is provided with all supported data types. Here are the supported data types:

- `STRING`
- `DOUBLE`
- `LONG`
- `DECIMAL`
- `DATE`
- `DATETIME`
- `TIME`

### Mappings

To correctly map your data to the chart, you must provide a mapping for each column. The `MAPPING` enum is used for this purpose. The following mappings are supported:

- `ITEM`: In a bar chart, this would be your x axis
- `VALUE`: In a bar chart, this would be your y axis
- `SERIES`: This is how your data is grouped

### Chart Properties

All Phoenix charts have default properties set to make your chart look great. You can override these properties, if desired. Examples of overrides include the chart's font size, whether or not to show the "Other" category, bar widths, and more. You can use them like so:

```javascript
const data = {
  // ...
};

const propertyOverrides = {
  font_size: 'Largest',
  hide_other_category: 'true',
  width_percentage: '50',
};

// Chart options
const options = {
  width: 600,
  height: 500,
  properties: propertyOverrides,
};

// Create the Phoenix Chart
const chart = new Chart(CHART_TYPE.VERT_BAR, data, options);

// Append the canvas element to your app
document.getElementById('myDiv').appendChild(chart.canvas);

// Render the chart when you're ready for the user to see it
chart.render();
```

By passing these options, your chart will be customized to those settings.

### Color Palettes

By default, the chart will use Domo's color palette. You can optionally specify your own custom color palette for your chart by passing an array of hex code strings in your options object. This example shows how to create a chart with a custom color palette of various shades of blue:

```javascript
const data = {
  // ...
};

const customColors = [
  '#002159',
  '#03449E',
  '#0967D2',
  '#47A3F3',
  '#BAE3FF'
];

// Chart Options
const options = {
  width: 600,
  height: 500
  colors: customColors
};

// Create the Phoenix Chart
const chart = new Chart(CHART_TYPE.VERT_BAR, data, options);

// Append the canvas element to your app
document.getElementById('myDiv').appendChild(chart.canvas);

// Render the chart when you're ready for the user to see it
chart.render();
```

You can pass as few or as many colors as you like in this array. Phoenix will start with the first color in the list and move down the array. If it runs out of colors, it will loop back to the beginning. For best visual results, provide enough different colors to cover the scope of your data.

To update your color palette or reset to the default, see the API documentation.

## Chart Methods

The following methods are supported in addition to those shown above:

### render()

This method performs the actual rendering of the chart on the canvas. Your chart will not appear until you have called this method.

```javascript
// Render chart
chart.render();
```

### resize(width, height)

The `resize` method allows you to resize your chart to any width and height (in pixels).

```javascript
// Resize chart to 800px by 500px
chart.resize(800, 500);
```

### update(data, options?)

The `update` method allows you to provide a new data object, which will update your chart to reflect those changes. **Note:** You do not need to call `render()` again; this method does that for you.

```javascript
// Get new data
const newData = {
  rows: [
    ['Michael Scott', 43],
    ['Jim Halpert', 36],
    ['Dwight Schrute', 41],
  ],
  columns: [
    {
      type: DATA_TYPE.STRING,
      name: 'Name',
      mapping: MAPPING.ITEM,
    },
    {
      type: DATA_TYPE.DOUBLE,
      name: 'Age',
      mapping: MAPPING.VALUE,
    },
  ],
};

// Update chart with new data
chart.update(newData);
```

You may also **optionally** provide the options object to the `update` method. In this object, you can pass an array of colors for a new color palette, as well as a map of chart property overrides, like so:

```javascript
// Get new data
const newData = {
  // ...
};

const options = {
  colors: ['#002159', '#03449E', '#0967D2', '#47A3F3'],
  properties: {
    'chart-property-1': 'value-1',
    'chart-property-2': 'value-2',
    'chart-property-3': 'value-3',
  },
};

// Update chart with new data as well as options providing a color palette and chart property overrides
chart.update(newData, options);
```

### setChartProperties(properties)

You can pass your chart new properties at any time and it will re-render accordingly. Simply pass an object of property keys and values to the method.

```javascript
// Define your properties
const properties = {
  'chart-property-1': 'value-1',
  'chart-property-2': 'value-2',
  'chart-property-3': 'value-3',
};
// Update chart with new properties
chart.setChartProperties(properties);
```

### resetColorPalette()

This method allows you to reset your chart's color palette back to the default Domo color palette. Your chart will automatically redraw with the Domo color palette.

```javascript
// Reset color palette to default
chart.resetColorPalette();
```

### addEventListener(type, (event) => boolean)

Attach a handler to various Phoenix event types. The following events are supported:

- `drill`
- `hover`
- `chartStateChanged`
- `cardbus`

```javascript
// Define your own drill "click" event
chart.addEventListener('drill', function (ev) {
  const filterStrings = ev.drillInfo.filters.map(
    (f) => `${f.column} contains ${f.values.join(' OR ')}`,
  );
  console.log('drilling on: ', filterStrings.join(' AND '));
  return true;
});
```

### setUsePhoenixHover(flag)

Have Phoenix render hover tooltips (`true` by default):

```javascript
// Disable Phoenix hover tooltips
chart.setUsePhoenixHover(false);
```
