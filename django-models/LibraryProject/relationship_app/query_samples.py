import os
import django

# --- Setup Django environment ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibraryProject.settings')
django.setup()

from relationship_app.models import Author, Book, Library, Librarian

# --- Create sample data ---

# Create Author
author, created = Author.objects.get_or_create(name="Chinua Achebe")
if created:
    print("✅ Author 'Chinua Achebe' created.")

# Create Library
library, created = Library.objects.get_or_create(name="Central Library", location="Lagos")
if created:
    print("✅ Library 'Central Library' created.")

# Create Librarian
librarian, created = Librarian.objects.get_or_create(name="Mrs. Obi", library=library)
if created:
    print("✅ Librarian 'Mrs. Obi' assigned to Central Library.")

# Create Books
book_titles = ["Things Fall Apart", "No Longer at Ease", "Arrow of God"]
for title in book_titles:
    book, created = Book.objects.get_or_create(title=title, author=author, library=library)
    if created:
        print(f"✅ Book '{title}' added.")

# --- Run sample queries ---

# Query all books by a specific author
author_name = "Chinua Achebe"
try:
    author = Author.objects.get(name=author_name)
    books_by_author = Book.objects.filter(author=author)
    print(f"\n📚 Books by {author_name}:")
    for book in books_by_author:
        print(f"- {book.title}")
except Author.DoesNotExist:
    print(f"No author found with name '{author_name}'")

# List all books in a specific library
library_name = "Central Library"
try:
    library = Library.objects.get(name=library_name)
    books_in_library = library.books.all()  
    print(f"\n🏛️ Books in {library_name}:")
    for book in books_in_library:
        print(f"- {book.title}")
except Library.DoesNotExist:
    print(f"No library found with name '{library_name}'")

# Retrieve the librarian for a library
try:
    library = Library.objects.get(name=library_name)
    librarian = Librarian.objects.get(library=library)
    print(f"\n👩‍🏫 Librarian for {library_name}: {librarian.name}")
except Library.DoesNotExist:
    print(f"\nCannot find librarian — library '{library_name}' was not found.")
except Librarian.DoesNotExist:
    print(f"\nNo librarian assigned to {library_name}")
