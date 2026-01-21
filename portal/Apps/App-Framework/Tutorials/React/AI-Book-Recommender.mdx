# AI Book Recommender App Tutorial

This tutorial will guide you through building an AI-powered book recommender app using React. By the end of this tutorial, you will have a fully functional app that suggests books based on user preferences. As you follow along, you will get experience doing a few things:

- Create a web app from scratch using Domo's React app template
- Pull book data from a public web API (Open Library)
- Get AI-generated text using Domo's AI Service Layer API

All code and files used for this tutorial can be found at [this GitHub repository](https://github.com/DomoApps/book-recommender-tutorial).

### Step 1: Setup and installation

---

Before beginning, please make sure you’ve successfully installed the Domo Apps CLI and followed the basic setup and installation instructions found [here](https://developer.domo.com/docs/dev-studio-quick-start/set-up). When following the article, please skip `Step 3: Create a New App`. We will be creating a React app instead of a simple Javascript app.

Initialize a React project using Domo's template by following the steps in [this article](https://developer.domo.com/portal/u8w475o2245yp-starter-kits).

Once your project has been created, open it in your preferred IDE and run `yarn` (or `npm install`) to install all required dependencies.

For this app, we are also going to install two extra libraries:

1. Ant Design - A popular React UI component library.
2. Ryuu.js - A Domo library for sending API requests to Domo.

Please install both of these by running `yarn add antd ryuu.js@4.2.0` (or `npm install antd ryuu.js@4.2.0`).

When you're ready, run `yarn start` (or `npm start`) to start developing locally.

### Step 2: Set up app components

---

Open the `public` and `src` folders to see the files that were auto-generated for you in Step 2. For this tutorial, we will only make changes to the `App.js` and `App.css`, and `manifest.json` files.

- `App.js` and `App.css` will contain the code to build the app and style it how we want.

- The `manifest.json` file is a special Domo file that is required for building apps on the Domo App Framework. [What is the manifest file?](https://developer.domo.com/portal/af407395c766b-the-manifest-file)

To start, we will update the contents of `App.js` to include a container div for our main app components. Replace everything inside of `App.js` with the following lines of code:

```js
import React from "react";
import "./App.css";

function App() {
  return (
    <div className="app">
      <div className="content">
        <div className="heading">
          <h1>Chapter One</h1>
          <h2>Find your next favorite book</h2>
        </div>
      </div>
    </div>
  );
}

export default App;
```

Then, replace everything in your `App.css` file with the following:

```css
.app {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  width: 100%;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 40%;
  padding: 40px;
  background-color: rgb(255, 255, 255);
}

.heading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  margin: 40px 0;
  font-family: serif;
}

.heading > h1 {
  text-transform: uppercase;
  font-size: 18px;
}

.heading > h2 {
  font-size: 40px;
}
```

Now, to make things look a little nicer, we're going to use a photo of a bookshelf for the app's background and add a chapter divider image to our content. You'll see it come together soon.

Please download the `bookshelf.jpeg` and `chapter_divider.png` files from the `public` folder in the project repo [here](https://github.com/DomoApps/book-recommender-tutorial).

Put both of these images in the `public` folder of your project.

Update your app div to use the bookshelf image as the background, and add the chapter divider image at the bottom of the heading container.

```js
<div
  className="app"
  style={{
    background: 'url("/bookshelf.jpeg") no-repeat center center fixed',
    backgroundSize: "cover",
    height: "100vh",
  }}
>
  <div className="content">
    <div className="heading">
      <h1>Chapter One</h1>
      <h2>Find your next favorite book</h2>
      <img
        style={{ marginTop: "30px" }}
        src="chapter_divider.png"
        width="40%"
      />
    </div>
  </div>
</div>
```

At this point, your app should look like this in the browser:

![screen-one.png](../../../../../assets/tutorials/book-recommender/screen-one.png)

### Step 3: Add Antd components for user interactivity

Now, let's add the state variables and components that will allow the user to choose their favorite books and their preferred genre, mood, and book length.

Start by adding these lines of code to the top of your component:

```js
import React, { useState } from "react";
import "./App.css";

function App() {
  const [favoriteBooks, setFavoriteBooks] = useState([]);
  const [genre, setGenre] = useState(undefined);
  const [mood, setMood] = useState(undefined);
  const [bookLength, setBookLength] = useState(undefined);
  ...
```

These state variables will hold the user input values.

Next, we'll add the Antd Select components so the user can choose their preferences. Add the components below the header.

```js
<div className="form">
  <Select
    mode="multiple"
    autoClearSearchValue
    filterOption={false}
    allowClear
    placeholder="Choose your favorite books"
    options={[{value: 'test', label: 'test'}]}
    style={{ flex: 1 }}
  />
</div>
<div className="form">
  <Select
    placeholder="Select a genre"
    options={[{value: 'test', label: 'test'}]}
    style={{ flex: 1 }}
  />
  <Select
    placeholder="Select a mood"
    options={[{value: 'test', label: 'test'}]}
    style={{ flex: 1 }}
  />
  <Select
    placeholder="Select a book length"
    options={[{value: 'test', label: 'test'}]}
    style={{ flex: 1 }}
  />
</div>
```

Also add this new class to your `App.css` file:

```css
.form {
  display: flex;
  gap: 8px;
}
```

Okay, now that we have our Select components, we need to add the lists of options we want to include in each dropdown. Let's start with the static options.

Add this code above your App component, below your imports:

```js
const genres = [
  { value: "adventure", label: "Adventure" },
  { value: "biography", label: "Biography" },
  { value: "business", label: "Business" },
  { value: "children", label: "Children" },
  { value: "classics", label: "Classics" },
  { value: "comics", label: "Comics" },
  { value: "cookbooks", label: "Cookbooks" },
  { value: "dystopian", label: "Dystopian" },
  { value: "fantasy", label: "Fantasy" },
  { value: "fiction", label: "Fiction" },
  { value: "graphic-novel", label: "Graphic Novel" },
  { value: "health", label: "Health" },
  { value: "historical", label: "Historical" },
  { value: "horror", label: "Horror" },
  { value: "memoir", label: "Memoir" },
  { value: "mystery", label: "Mystery" },
  { value: "non-fiction", label: "Non-Fiction" },
  { value: "philosophy", label: "Philosophy" },
  { value: "poetry", label: "Poetry" },
  { value: "romance", label: "Romance" },
  { value: "science-fiction", label: "Science Fiction" },
  { value: "self-help", label: "Self-Help" },
  { value: "spirituality", label: "Spirituality" },
  { value: "thriller", label: "Thriller" },
  { value: "travel", label: "Travel" },
  { value: "true-crime", label: "True Crime" },
  { value: "young-adult", label: "Young Adult" },
];

const moods = [
  { value: "adventurous", label: "Adventurous" },
  { value: "dark", label: "Dark" },
  { value: "funny", label: "Funny" },
  { value: "happy", label: "Happy" },
  { value: "inspirational", label: "Inspirational" },
  { value: "intense", label: "Intense" },
  { value: "mysterious", label: "Mysterious" },
  { value: "nostalgic", label: "Nostalgic" },
  { value: "reflective", label: "Reflective" },
  { value: "relaxing", label: "Relaxing" },
  { value: "romantic", label: "Romantic" },
  { value: "sad", label: "Sad" },
  { value: "suspenseful", label: "Suspenseful" },
  { value: "thought-provoking", label: "Thought-Provoking" },
  { value: "uplifting", label: "Uplifting" },
  { value: "whimsical", label: "Whimsical" },
];

const bookLengths = [
  { value: "short", label: "Short (Less than 200 pages)" },
  { value: "medium", label: "Medium (200-400 pages)" },
  { value: "long", label: "Long (More than 400 pages)" },
  { value: "epic", label: "Epic (More than 600 pages)" },
  { value: "novella", label: "Novella (50-100 pages)" },
  { value: "series", label: "Series (Multiple books)" },
];
```

Now, you can update the `options` prop for each of the Select components to reference these const variables.

We'll also go ahead and wire the `value` prop to our state variables, and implement the `onChange` event for each static Select component.

```js
<div className="form">
  <Select
    placeholder="Select a genre"
    value={genre}
    onChange={(value) => setGenre(value)}
    options={genres}
    style={{ flex: 1 }}
  />
  <Select
    placeholder="Select a mood"
    value={mood}
    onChange={(value) => setMood(value)}
    options={moods}
    style={{ flex: 1 }}
  />
  <Select
    placeholder="Select a book length"
    value={bookLength}
    onChange={(value) => setBookLength(value)}
    options={bookLengths}
    style={{ flex: 1 }}
  />
</div>
```

You should now be able to see our static options in the dropdown for each of the bottom three Select components and the user can make a selection.

![screen-two.png](../../../../../assets/tutorials/book-recommender/screen-two.png)

### Step 4: Fetch books from Open Library API

We are going to dynamically fetch books from Open Library's free public API so that the user can enter a few of their favorite books. This will give extra context to our AI model when we generate recommendations.

When the user starts typing in the "Choose your favorite books" box, we'll send a request to the API to fetch books that match the title given by the user. Then we'll display the list of books for the user to select from.

Let's start implementing this by creating a function to call Open Library's API.

```js
const fetchBooks = async (query) => {
  const url = `https://openlibrary.org/search.json?title=${encodeURIComponent(query)}`;
  const response = await fetch(url);
  const data = await response.json();
  return data.docs;
};

return (
  <div
    className="app"
    ...
```

Now, let's write some logic to debounce the input change event and call our new function when we're ready to search for books. We'll also add two new state variables, `allBooks` and `matchingBooks`, to keep track of our fetched books.

We'll memoize `matchingBooks` and build a book option array that is formatted with the information we want to display in our Select component.

```js
const [allBooks, setAllBooks] = useState([]);
const [matchingBooks, setMatchingBooks] = useState([]);

const bookOptions = useMemo(
  () =>
    matchingBooks.map((book) => ({
      value: book.key,
      label: `${book.title}, ${
        book.author_name?.join(", ") || "Unknown Author"
      }`,
    })),
  [matchingBooks]
);

const fetchBooks = async (query) => {
  const url = `https://openlibrary.org/search.json?title=${encodeURIComponent(query)}`;
  const response = await fetch(url);
  const data = await response.json();
  return data.docs;
};

const debounceTimer = useRef(null);

const onBookSearch = async (value) => {
  if (debounceTimer.current) {
    clearTimeout(debounceTimer.current);
  }
  debounceTimer.current = setTimeout(async () => {
    const fetchedBooks = await fetchBooks(value);
    setMatchingBooks(fetchedBooks);
    setAllBooks((prevBooks) => [
      ...prevBooks,
      ...fetchedBooks.filter(
        (newBook) => !prevBooks.some((book) => book.key === newBook.key),
      ),
    ]);
  }, 300); // Adjust debounce delay as needed
};

return (
  <div
    className="app"
    ...
```

We'll also need an onChange handler for when the user clicks on one or more books in the list.

```js
const onBookChange = async (value) => {
  const selectedBooks = allBooks.filter((book) => value.includes(book.key));
  setFavoriteBooks(selectedBooks);
};
```

With that, we can wire up these handlers to our "Favorite Books" Select component.

```js
<Select
  mode="multiple"
  autoClearSearchValue
  filterOption={false}
  allowClear
  placeholder="Choose your favorite books"
  value={favoriteBooks.map((book) => book.key)}
  onSearch={onBookSearch}
  onChange={onBookChange}
  options={bookOptions}
  style={{ flex: 1 }}
/>
```

At this point your `App.js` file should look like this:

```js
import React, { useMemo, useState, useRef } from "react";
import { Select } from "antd";
import "./App.css";

const genres = [
  { value: "adventure", label: "Adventure" },
  { value: "biography", label: "Biography" },
  { value: "business", label: "Business" },
  { value: "children", label: "Children" },
  { value: "classics", label: "Classics" },
  { value: "comics", label: "Comics" },
  { value: "cookbooks", label: "Cookbooks" },
  { value: "dystopian", label: "Dystopian" },
  { value: "fantasy", label: "Fantasy" },
  { value: "fiction", label: "Fiction" },
  { value: "graphic-novel", label: "Graphic Novel" },
  { value: "health", label: "Health" },
  { value: "historical", label: "Historical" },
  { value: "horror", label: "Horror" },
  { value: "memoir", label: "Memoir" },
  { value: "mystery", label: "Mystery" },
  { value: "non-fiction", label: "Non-Fiction" },
  { value: "philosophy", label: "Philosophy" },
  { value: "poetry", label: "Poetry" },
  { value: "romance", label: "Romance" },
  { value: "science-fiction", label: "Science Fiction" },
  { value: "self-help", label: "Self-Help" },
  { value: "spirituality", label: "Spirituality" },
  { value: "thriller", label: "Thriller" },
  { value: "travel", label: "Travel" },
  { value: "true-crime", label: "True Crime" },
  { value: "young-adult", label: "Young Adult" },
];

const moods = [
  { value: "adventurous", label: "Adventurous" },
  { value: "dark", label: "Dark" },
  { value: "funny", label: "Funny" },
  { value: "happy", label: "Happy" },
  { value: "inspirational", label: "Inspirational" },
  { value: "intense", label: "Intense" },
  { value: "mysterious", label: "Mysterious" },
  { value: "nostalgic", label: "Nostalgic" },
  { value: "reflective", label: "Reflective" },
  { value: "relaxing", label: "Relaxing" },
  { value: "romantic", label: "Romantic" },
  { value: "sad", label: "Sad" },
  { value: "suspenseful", label: "Suspenseful" },
  { value: "thought-provoking", label: "Thought-Provoking" },
  { value: "uplifting", label: "Uplifting" },
  { value: "whimsical", label: "Whimsical" },
];

const bookLengths = [
  { value: "short", label: "Short (Less than 200 pages)" },
  { value: "medium", label: "Medium (200-400 pages)" },
  { value: "long", label: "Long (More than 400 pages)" },
  { value: "epic", label: "Epic (More than 600 pages)" },
  { value: "novella", label: "Novella (50-100 pages)" },
  { value: "series", label: "Series (Multiple books)" },
];

function App() {
  const [favoriteBooks, setFavoriteBooks] = useState([]);
  const [genre, setGenre] = useState(undefined);
  const [mood, setMood] = useState(undefined);
  const [bookLength, setBookLength] = useState(undefined);

  const [allBooks, setAllBooks] = useState([]);
  const [matchingBooks, setMatchingBooks] = useState([]);

  const bookOptions = useMemo(
    () =>
      matchingBooks.map((book) => ({
        value: book.key,
        label: `${book.title}, ${
          book.author_name?.join(", ") || "Unknown Author"
        }`,
      })),
    [matchingBooks]
  );

  const fetchBooks = async (query) => {
    const url = `https://openlibrary.org/search.json?title=${encodeURIComponent(
      query
    )}`;
    const response = await fetch(url);
    const data = await response.json();
    return data.docs;
  };

  const debounceTimer = useRef(null);

  const onBookSearch = async (value) => {
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }
    debounceTimer.current = setTimeout(async () => {
      const fetchedBooks = await fetchBooks(value);
      setMatchingBooks(fetchedBooks);
      setAllBooks((prevBooks) => [
        ...prevBooks,
        ...fetchedBooks.filter(
          (newBook) => !prevBooks.some((book) => book.key === newBook.key)
        ),
      ]);
    }, 300); // Adjust debounce delay as needed
  };

  const onBookChange = async (value) => {
    const selectedBooks = allBooks.filter((book) => value.includes(book.key));
    setFavoriteBooks(selectedBooks);
  };

  return (
    <div
      className="app"
      style={{
        background: 'url("/bookshelf.jpeg") no-repeat center center fixed',
        backgroundSize: "cover",
        height: "100vh",
      }}
    >
      <div className="content">
        <div className="heading">
          <h1>Chapter One</h1>
          <h2>Find your next favorite book</h2>
          <img
            style={{ marginTop: "30px" }}
            src="chapter_divider.png"
            width="40%"
          />
        </div>
        <div className="form">
          <Select
            mode="multiple"
            autoClearSearchValue
            filterOption={false}
            allowClear
            placeholder="Choose your favorite books"
            options={bookOptions}
            value={favoriteBooks.map((book) => book.key)}
            onSearch={onBookSearch}
            onChange={onBookChange}
            style={{ flex: 1 }}
          />
        </div>
        <div className="form">
          <Select
            placeholder="Select a genre"
            value={genre}
            onChange={(value) => setGenre(value)}
            options={genres}
            style={{ flex: 1 }}
          />
          <Select
            placeholder="Select a mood"
            value={mood}
            onChange={(value) => setMood(value)}
            options={moods}
            style={{ flex: 1 }}
          />
          <Select
            placeholder="Select a book length"
            value={bookLength}
            onChange={(value) => setBookLength(value)}
            options={bookLengths}
            style={{ flex: 1 }}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
```

Look at your app running in the browser.

When you start typing into the first Select component to choose your favorite book(s), a request is being sent to the Open Library API. You should see a list of options appear in the dropdown based on your search.

### Step 5: Using DomoGPT to get book recommendations

---

Now for the most exciting part: connecting to Domo's AI Service Layer!

We want to bundle up all of the user input, send it to our AI model, and get back a list of recommended books that the user is sure to love.

Let's start by importing `domo` from `ryuu.js` so we can send API requests to Domo. Add this line at the top of `App.js`:

```js
import domo from "ryuu.js";
```

Next, we'll write the function to send the API request to the AI Service Layer. We'll be using the `text generation` endpoint to generate our book recommendations. To learn more about the other services available with Domo's AI Service Layer, check out our article on [Domo's AI Playground](https://domo-support.domo.com/s/article/000005236?language=en_US).

```js
const userPrompt = ``;
const systemPrompt = ``;

const getBookRecommendations = async (books, genre, mood, bookLength) => {
  try {
    const bookInfo = books
      .map((book) => {
        return `**${book.title}** by ${
          book.author_name?.join(", ") || "Unknown Author"
        }`;
      })
      .join(", ");

    const body = {
      input: `Favorite Books: ${bookInfo}, Genre: ${genre || "Any"}, Mood: ${
        mood || "Any"
      }, Length: ${bookLength || "Any"}`,
      promptTemplate: {
        template: `${userPrompt} \`\`\`\${input}\`\`\``,
      },
      system: systemPrompt,
      outputWordLength: {
        max: 400,
      },
    };

    const data = await domo.post(`/domo/ai/v1/text/generation`, body);
    const output = data.choices[0].output;
    return JSON.parse(output);
  } catch (error) {
    console.error("Error processing chunk:", error);
    return [];
  }
};
```

The quality of responses you get from an AI model are heavily dependent on the context you provide and the prompts you pass in. We are going to pass in a pre-defined user prompt as part of our request, as well as a detailed system prompt that describes the role of our AI.

You can start with the prompts we provide. Feel free to experiment with different prompts.

```js
const userPrompt = `Please generate a list of book recommendations based on the user's preferences.`;

const systemPrompt = `
You are a helpful, well-read literary assistant who gives thoughtful book recommendations.

The user will provide:
- A list of their favorite books (including author names if available)
- The genre(s) they're interested in
- The mood or tone they're looking for (e.g., uplifting, dark, relaxing, intense)
- Their preferred book length (e.g., short reads, medium, long epics)

Your task is to analyze the user's preferences and recommend **4 books** that:
- Match their genre, mood, and length preferences
- Share themes, tone, writing style, or emotional resonance with their favorite books
- Are not already listed in their favorites

For each recommendation, include:
- Title
- Author
- 1-2 sentence explanation of why it was chosen, referencing the user's input

Prioritize well-reviewed books, lesser-known gems, and avoid overly generic picks unless they are a perfect match.

If a user gives few inputs, do your best to infer recommendations from what's provided.

**Output format:**

Please return a JSON array of objects, each containing:
- "title": The title of the book
- "author": The author of the book
- "reason": A brief explanation of why this book was recommended

Do not include any additional text or explanations outside of this JSON format.`;
```

The last thing we need to do is call our new `getBookRecommendations` function and display the AI-generated results.

Add a new Button component below our form components:

```js
  ...
  <Select
    placeholder="Select a book length"
    value={bookLength}
    onChange={(value) => setBookLength(value)}
    options={bookLengths}
    style={{ flex: 1 }}
  />
</div>
<Button onClick={onSubmit} loading={loading}>
  Get Recommendations
</Button>
```

You'll import the Button component from the `antd` library, the same way you import the Select component.

```js
import { Button, Select } from "antd";
```

Now, let's implement the `onSubmit` function and create two new state variables: `loading` (so we can show a loading indicator when the button is clicked), and `recommendations` (to hold the AI-generated book recommendations).

```js
const [recommendations, setRecommendations] = useState([]);
const [loading, setLoading] = useState(false);

...

const onSubmit = async () => {
  setLoading(true);
  const recs = await getBookRecommendations(
    favoriteBooks,
    genre,
    mood,
    bookLength,
  );
  setRecommendations(recs);
  setLoading(false);
};
```

Then, we'll simply conditionally display the recommendations as soon as they've been generated.

```js
<div className="recommendations">
  <h1>Recommended Books</h1>
  <div className="bookList">
    {recommendations.map((rec, index) => (
      <div key={index} className="bookItem">
        <h4>{rec.title}</h4>
        <p className="author">{rec.author}</p>
        <p className="reason">{rec.reason}</p>
      </div>
    ))}
  </div>
</div>
```

Add these new styles to `App.css`:

```css
.recommendations > h1 {
  font-family: serif;
}

.bookList {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-top: 20px;
}

.bookItem {
  padding: 15px;
  background-color: rgb(242, 242, 242);
  border-radius: 6px;
}

.bookItem > h4 {
  line-height: 18px;
}

.author {
  margin: 5px 0;
  font-size: 14px;
  line-height: 16px;
  color: rgb(19, 99, 62);
}

.reason {
  margin: 10px 0;
  font-size: 14px;
}
```

Your finished `App.js` file should now look something like this:

```js
import React, { useMemo, useState, useRef } from "react";
import { Button, Select } from "antd";
import domo from "ryuu.js";
import "./App.css";

const userPrompt = `Please generate a list of book recommendations based on the user's preferences.`;

const systemPrompt = `
You are a helpful, well-read literary assistant who gives thoughtful book recommendations.

The user will provide:
- A list of their favorite books (including author names if available)
- The genre(s) they're interested in
- The mood or tone they're looking for (e.g., uplifting, dark, relaxing, intense)
- Their preferred book length (e.g., short reads, medium, long epics)

Your task is to analyze the user's preferences and recommend **4 books** that:
- Match their genre, mood, and length preferences
- Share themes, tone, writing style, or emotional resonance with their favorite books
- Are not already listed in their favorites

For each recommendation, include:
- Title
- Author
- 1-2 sentence explanation of why it was chosen, referencing the user's input

Prioritize well-reviewed books, lesser-known gems, and avoid overly generic picks unless they are a perfect match.

If a user gives few inputs, do your best to infer recommendations from what's provided.

**Output format:**

Please return a JSON array of objects, each containing:
- "title": The title of the book
- "author": The author of the book
- "reason": A brief explanation of why this book was recommended

Do not include any additional text or explanations outside of this JSON format.`;

const genres = [
  { value: "adventure", label: "Adventure" },
  { value: "biography", label: "Biography" },
  { value: "business", label: "Business" },
  { value: "children", label: "Children" },
  { value: "classics", label: "Classics" },
  { value: "comics", label: "Comics" },
  { value: "cookbooks", label: "Cookbooks" },
  { value: "dystopian", label: "Dystopian" },
  { value: "fantasy", label: "Fantasy" },
  { value: "fiction", label: "Fiction" },
  { value: "graphic-novel", label: "Graphic Novel" },
  { value: "health", label: "Health" },
  { value: "historical", label: "Historical" },
  { value: "horror", label: "Horror" },
  { value: "memoir", label: "Memoir" },
  { value: "mystery", label: "Mystery" },
  { value: "non-fiction", label: "Non-Fiction" },
  { value: "philosophy", label: "Philosophy" },
  { value: "poetry", label: "Poetry" },
  { value: "romance", label: "Romance" },
  { value: "science-fiction", label: "Science Fiction" },
  { value: "self-help", label: "Self-Help" },
  { value: "spirituality", label: "Spirituality" },
  { value: "thriller", label: "Thriller" },
  { value: "travel", label: "Travel" },
  { value: "true-crime", label: "True Crime" },
  { value: "young-adult", label: "Young Adult" },
];

const moods = [
  { value: "adventurous", label: "Adventurous" },
  { value: "dark", label: "Dark" },
  { value: "funny", label: "Funny" },
  { value: "happy", label: "Happy" },
  { value: "inspirational", label: "Inspirational" },
  { value: "intense", label: "Intense" },
  { value: "mysterious", label: "Mysterious" },
  { value: "nostalgic", label: "Nostalgic" },
  { value: "reflective", label: "Reflective" },
  { value: "relaxing", label: "Relaxing" },
  { value: "romantic", label: "Romantic" },
  { value: "sad", label: "Sad" },
  { value: "suspenseful", label: "Suspenseful" },
  { value: "thought-provoking", label: "Thought-Provoking" },
  { value: "uplifting", label: "Uplifting" },
  { value: "whimsical", label: "Whimsical" },
];

const bookLengths = [
  { value: "short", label: "Short (Less than 200 pages)" },
  { value: "medium", label: "Medium (200-400 pages)" },
  { value: "long", label: "Long (More than 400 pages)" },
  { value: "epic", label: "Epic (More than 600 pages)" },
  { value: "novella", label: "Novella (50-100 pages)" },
  { value: "series", label: "Series (Multiple books)" },
];

function App() {
  const [favoriteBooks, setFavoriteBooks] = useState([]);
  const [genre, setGenre] = useState(undefined);
  const [mood, setMood] = useState(undefined);
  const [bookLength, setBookLength] = useState(undefined);

  const [allBooks, setAllBooks] = useState([]);
  const [matchingBooks, setMatchingBooks] = useState([]);

  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  const bookOptions = useMemo(
    () =>
      matchingBooks.map((book) => ({
        value: book.key,
        label: `${book.title}, ${
          book.author_name?.join(", ") || "Unknown Author"
        }`,
      })),
    [matchingBooks]
  );

  const fetchBooks = async (query) => {
    const url = `https://openlibrary.org/search.json?title=${encodeURIComponent(
      query
    )}`;
    const response = await fetch(url);
    const data = await response.json();
    return data.docs;
  };

  const debounceTimer = useRef(null);

  const onBookSearch = async (value) => {
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }
    debounceTimer.current = setTimeout(async () => {
      const fetchedBooks = await fetchBooks(value);
      setMatchingBooks(fetchedBooks);
      setAllBooks((prevBooks) => [
        ...prevBooks,
        ...fetchedBooks.filter(
          (newBook) => !prevBooks.some((book) => book.key === newBook.key)
        ),
      ]);
    }, 300); // Adjust debounce delay as needed
  };

  const onBookChange = async (value) => {
    const selectedBooks = allBooks.filter((book) => value.includes(book.key));
    setFavoriteBooks(selectedBooks);
  };

  const getBookRecommendations = async (books, genre, mood, bookLength) => {
    try {
      const bookInfo = books
        .map((book) => {
          return `**${book.title}** by ${
            book.author_name?.join(", ") || "Unknown Author"
          }`;
        })
        .join(", ");

      const body = {
        input: `Favorite Books: ${bookInfo}, Genre: ${genre || "Any"}, Mood: ${
          mood || "Any"
        }, Length: ${bookLength || "Any"}`,
        promptTemplate: {
          template: `${userPrompt} \`\`\`\${input}\`\`\``,
        },
        system: systemPrompt,
        outputWordLength: {
          max: 400,
        },
      };

      const data = await domo.post(`/domo/ai/v1/text/generation`, body);
      const output = data.choices[0].output;
      return JSON.parse(output);
    } catch (error) {
      console.error("Error processing chunk:", error);
      return [];
    }
  };

  const onSubmit = async () => {
    setLoading(true);
    const recs = await getBookRecommendations(
      favoriteBooks,
      genre,
      mood,
      bookLength
    );
    setRecommendations(recs);
    setLoading(false);
  };

  return (
    <div
      className="app"
      style={{
        background: 'url("/bookshelf.jpeg") no-repeat center center fixed',
        backgroundSize: "cover",
        height: "100vh",
      }}
    >
      <div className="content">
        {recommendations.length === 0 ? (
          <>
            <div className="heading">
              <h1>Chapter One</h1>
              <h2>Find your next favorite book</h2>
              <img
                style={{ marginTop: "30px" }}
                src="chapter_divider.png"
                width="40%"
              />
            </div>
            <div className="form">
              <Select
                mode="multiple"
                autoClearSearchValue
                filterOption={false}
                allowClear
                placeholder="Choose your favorite books"
                options={bookOptions}
                value={favoriteBooks.map((book) => book.key)}
                onSearch={onBookSearch}
                onChange={onBookChange}
                style={{ flex: 1 }}
              />
            </div>
            <div className="form">
              <Select
                placeholder="Select a genre"
                value={genre}
                onChange={(value) => setGenre(value)}
                options={genres}
                style={{ flex: 1 }}
              />
              <Select
                placeholder="Select a mood"
                value={mood}
                onChange={(value) => setMood(value)}
                options={moods}
                style={{ flex: 1 }}
              />
              <Select
                placeholder="Select a book length"
                value={bookLength}
                onChange={(value) => setBookLength(value)}
                options={bookLengths}
                style={{ flex: 1 }}
              />
            </div>
            <Button onClick={onSubmit} loading={loading}>
              Get Recommendations
            </Button>
          </>
        ) : (
          <div>
            <h1>Recommended Books</h1>
            <div className="bookList">
              {recommendations.map((rec, index) => (
                <div key={index} className="bookItem">
                  <h4>{rec.title}</h4>
                  <p className="author">{rec.author}</p>
                  <p className="reason">{rec.reason}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
```

![screen-three.png](../../../../../assets/tutorials/book-recommender/screen-three.png)

![screen-four.png](../../../../../assets/tutorials/book-recommender/screen-four.png)

Congratulations! You've now successfully built a React app that uses Domo's AI Service Layer to generate text based on user input.

There are so many possibilities when it comes to using AI in conjunction with Domo's App Framework. We make it easy for you to send requests to any of the models you've connected in your Domo instance.

Review our docs for the [AI Service Layer API](https://developer.domo.com/portal/wjqiqhsvpadon-ai-service-layer-api) to find out what else you can do.
