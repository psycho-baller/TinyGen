import type { Header } from "~types/config";

export const headerRoutes: Header[] = [
	{
		id: 1,
		title: "Home",
		newTab: false,
		path: "/",
	},
	{
		id: 2,
		title: "Features",
		newTab: false,
		path: "/#features",
	},
	{
		id: 3,
		title: "Demo",
		newTab: false,
		path: "/#demo",
	},
	// {
	//   id: 2.1,
	//   title: "Blog",
	//   newTab: false,
	//   path: "/blog"
	// },
	// {
	//   id: 2.3,
	//   title: "Docs",
	//   newTab: false,
	//   path: "/docs"
	// },
	// {
	//   id: 3,
	//   title: "Pages",
	//   newTab: false,
	//   submenu: [
	//     {
	//       id: 31,
	//       title: "Blog Grid",
	//       newTab: false,
	//       path: "/blog",
	//     },
	//     {
	//       id: 34,
	//       title: "Sign In",
	//       newTab: false,
	//       path: "/auth/signin",
	//     },
	//     {
	//       id: 35,
	//       title: "Sign Up",
	//       newTab: false,
	//       path: "/auth/signup",
	//     },
	//     {
	//       id: 35,
	//       title: "Docs",
	//       newTab: false,
	//       path: "/docs",
	//     },
	//     {
	//       id: 35.1,
	//       title: "Support",
	//       newTab: false,
	//       path: "/support",
	//     },
	//     {
	//       id: 36,
	//       title: "404",
	//       newTab: false,
	//       path: "/error",
	//     },
	//   ],
	// },

	{
		id: 4,
		title: "Contact",
		newTab: false,
		path: "/contact",
	},
	{
		id: 5,
		title: "API Documentation",
		newTab: false,
		path: "/api/docs",
	},
];
