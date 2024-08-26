
Django Blog 
Staff korisnici imaju potpuni pristup za upravljanje postovima i komentarima, dok korisnici koji nemaju staff status mogu samo komentarisati postove, ažurirati svoje komentare i brisati ih.

Koristio sam Django i Django REST framework.

# Endpoints

# Blog Postovi

- `GET /blogposts/` - Prikazuje sve blog postove.
- `POST /blogposts/` - Kreira novi blog post. (Samo za ulogovane administratore.)
 {
        "title": "Novi naslov",
        "content": "Novi sadržaj"
    }

- `GET /blogposts/<int:pk>/` - Prikazuje detalje o blog postu
- `PUT /blogposts/<int:pk>/` - Azurira odredjeni blog post. (Samo za ulogovane administratore.)
 {
        "title": "Azuriran naslov",
        "content": "Azuriran sadržaj"
    }
- `DELETE /blogposts/<int:pk>/` - Brise odredjeni blog post. (Samo za ulogovane administratore.)

# Komentari

- `GET /blogposts/<int:pk>/comments/` - Prikazuje sve komentare za odredjeni blog post.
- `POST /blogposts/<int:pk>/comments/` - Dodaje novi komentar na odredjeni blog post. (Samo za ulogovane korisnike.)
{
        "content": "Ovo je novi komentar"
    }

- `GET /comments/<int:id>/` - Prikazuje detalje o određenom komentaru.
- `PUT /comments/<int:id>/` - Azurira odredjeni komentar. (Samo za ulogovane korisnike koji su autori komentara.)
{
    "content": "Ažurirani komentar"
}
- `DELETE /comments/<int:id>/` - Brise odredjeni komentar. (Samo za ulogovane korisnike koji su autori komentara.)

# Korisnici

- `POST /register_user/` - Registruje novog korisnika.
- `POST /login_user/` - Prijavljuje korisnika.
- `POST /logout_user/` - Odjavljuje korisnika.


