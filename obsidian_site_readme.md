in "C:\Users\Zoom\My Drive (hello@causalmap.app)\causal-blog-flowershow\content" there is an Obsidian repo. we are going to use it to make a simple static site, like flowershow and quartz do, with left-side collapsible navigation with folders and subfolders, initially collapse to the top level. initially show index.md as the home page. write a script to do this in python.

Only include folders which begin with a number, and don't include files in the root except for index.md
Don't show the filename as title of the main content.
use the first heading (h1 h2 etc) of the content as the title in the sidebar and for the html page. but keep ordering the folders and their contents in alphanumeric sort of the filenames
and strip the numbers from the folders in the sidebar
add a light, academic style with plenty of padding around body 

good but more padding, sidebar much wider, slightly larger fonts everywhere. 
obsidian's internal links like: [[link]]. present them as a light collapsible div, titled with the title, closed by default, but which opens the text of the referred page on click

on clicking a file in sidebar, don't close folder, leave it open and highlight the file. 
for pages with more than one heading, add a On this Page right sidebar with clickable ToC