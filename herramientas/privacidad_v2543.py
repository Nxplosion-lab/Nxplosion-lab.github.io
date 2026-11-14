#!/usr/bin/env python3
"""PH 2.5.43 (14-11-2026): la política de privacidad, al día con la app y con lo declarado a Google Play.
- Sin chat ni grupos (se retiraron de la app en la 2.4; la ficha de Play ya lo dice).
- Apartado 9: lo que se borra y lo que se conserva, tal como lo hace ahora deleteMyData (servidor 2.5.43).
- Apartado 11: no dirigida a menores de 13 (público de Play 13+), con el permiso de los padres por debajo de 14.
Cambia los bloques 1, 12, 14, 16, 24, 25, 28 y 29 de privacy_html (contando <p> y <li> en orden) y la fecha.
Uso: python3 herramientas/privacidad_v2543.py && python3 herramientas/generar_web.py"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
TX = os.path.join(HERE, 'web', 'textos')
FB = 'Google Firebase (Google Cloud'

T = {
'es': {
 1: "Platinum Hunter muestra los trofeos de tu cuenta de PlayStation Network. La mayor parte funciona solo en tu dispositivo,\nque se comunica con los servidores de Sony. Las funciones de comunidad (Nivel Hunter y rankings, consejos, reseñas, valoraciones\ny la copia en la nube) usan nuestro servidor, alojado en Google Firebase (Google Cloud, región de la Unión Europea, Bélgica).\nSolo se activan si verificas tu cuenta en la app. La app no tiene chat ni grupos propios.",
 12: "<strong>Lo que publicas:</strong> consejos, votos, valoraciones de juegos (dificultad, horas y nota), reseñas y votos de «ya no se puede conseguir».",
 14: "<strong>Avisos:</strong> si los activas, un identificador de notificaciones de Firebase Cloud Messaging para que el servidor pueda enviarte avisos.",
 16: "Tu ID online, avatar, nivel, puntos y país, y lo que publicas, son visibles para otros usuarios en los rankings y en la comunidad.",
 24: "<strong>Se borran:</strong> tu ranking y tu progreso, tu copia en la nube, tus reseñas, consejos, valoraciones y horas de juego, tus votos,\nlas denuncias que hiciste, tus bloqueos y tu cuenta del servidor.",
 25: "<strong>Se conserva:</strong> solo el recuento anónimo de denuncias del contenido de otros, sin quién denunció, para que lo que ya se ocultó siga oculto, mientras exista ese contenido.\nSi escribiste en grupos de otros en versiones antiguas de la app, esos mensajes quedan anónimos y sin texto.\nLos informes de fallos de Crashlytics se borran solos a los 90 días.",
 28: "Platinum Hunter no está dirigida a menores de 13 años.",
 29: "Las funciones de comunidad (ranking, copia en la nube, consejos y reseñas) guardan datos en nuestro servidor. Si tienes menos de 14 años (o la edad que fije la ley de tu país), necesitas el permiso de tu padre, madre o tutor para usarlas y para aceptar anuncios personalizados, que puedes rechazar en el aviso de consentimiento o en los ajustes de la app. Si sabemos que alguien por debajo de esa edad usa la comunidad sin ese permiso, borramos sus datos del servidor.",
},
'es-419': {
 1: "Platinum Hunter muestra los trofeos de tu cuenta de PlayStation Network. La mayor parte funciona solo en tu dispositivo,\nque se comunica con los servidores de Sony. Las funciones de comunidad (Nivel Hunter y rankings, consejos, reseñas, calificaciones\ny la copia en la nube) usan nuestro servidor, alojado en Google Firebase (Google Cloud, región de la Unión Europea, Bélgica).\nSolo se activan si verificas tu cuenta en la app. La app no tiene chat ni grupos propios.",
 12: "<strong>Lo que publicas:</strong> consejos, votos, valoraciones de juegos (dificultad, horas y calificación), reseñas y votos de «ya no se puede conseguir».",
 14: "<strong>Avisos:</strong> si los activas, un identificador de notificaciones de Firebase Cloud Messaging para que el servidor pueda enviarte avisos.",
 16: "Tu ID online, avatar, nivel, puntos y país, y lo que publicas, son visibles para otros usuarios en los rankings y en la comunidad.",
 24: "<strong>Se borran:</strong> tu ranking y tu progreso, tu copia en la nube, tus reseñas, consejos, calificaciones y horas de juego, tus votos,\nlos reportes que hiciste, tus bloqueos y tu cuenta del servidor.",
 25: "<strong>Se conserva:</strong> solo el conteo anónimo de reportes del contenido de otros, sin quién reportó, para que lo que ya se ocultó siga oculto, mientras exista ese contenido.\nSi escribiste en grupos de otros en versiones antiguas de la app, esos mensajes quedan anónimos y sin texto.\nLos informes de fallas de Crashlytics se borran solos a los 90 días.",
 28: "Platinum Hunter no está dirigida a menores de 13 años.",
 29: "Las funciones de comunidad (ranking, copia en la nube, consejos y reseñas) guardan datos en nuestro servidor. Si tienes menos de 14 años (o la edad que fije la ley de tu país), necesitas el permiso de tu padre, madre o tutor para usarlas y para aceptar anuncios personalizados, que puedes rechazar en el aviso de consentimiento o en los ajustes de la app. Si sabemos que alguien por debajo de esa edad usa la comunidad sin ese permiso, borramos sus datos del servidor.",
},
'en': {
 1: "Platinum Hunter shows the trophies of your PlayStation Network account. Most of it works only on your device,\nwhich talks to Sony's servers. The community features (Hunter Level and rankings, tips, reviews, ratings\nand the cloud backup) use our server, hosted on Google Firebase (Google Cloud, European Union region, Belgium).\nThey are only turned on if you verify your account in the app. The app has no chat or groups of its own.",
 12: "<strong>What you post:</strong> tips, votes, game ratings (difficulty, hours and score), reviews and “Can it no longer be earned?” votes.",
 14: "<strong>Notifications:</strong> if you turn them on, a Firebase Cloud Messaging notification ID so the server can send you notifications.",
 16: "Your online ID, avatar, level, points and country, and what you post, are visible to other users in the rankings and in the community.",
 24: "<strong>Deleted:</strong> your ranking and progress, your cloud backup, your reviews, tips, ratings and play hours, your votes,\nthe reports you made, your blocks and your server account.",
 25: "<strong>Kept:</strong> only the anonymous count of reports on other people's content, without who reported it, so that what was already hidden stays hidden, for as long as that content exists.\nIf you wrote in other people's groups in old versions of the app, those messages stay anonymous and without text.\nCrashlytics crash reports are deleted automatically after 90 days.",
 28: "Platinum Hunter is not directed at children under 13.",
 29: "The community features (ranking, cloud backup, tips and reviews) store data on our server. If you are under 14 (or the age set by the law of your country), you need permission from your parent or guardian to use them and to accept personalised ads, which you can refuse in the consent notice or in the app settings. If we learn that someone below that age is using the community without that permission, we delete their data from the server.",
},
'fr': {
 1: "Platinum Hunter affiche les trophées de ton compte PlayStation Network. L'essentiel fonctionne uniquement sur ton appareil,\nqui communique avec les serveurs de Sony. Les fonctions communautaires (Niveau Hunter et classements, astuces, critiques, évaluations\net la sauvegarde cloud) utilisent notre serveur, hébergé sur Google Firebase (Google Cloud, région Union européenne, Belgique).\nElles ne s'activent que si tu vérifies ton compte dans l'app. L'app n'a ni discussion ni groupes propres.",
 12: "<strong>Ce que tu publies :</strong> astuces, votes, évaluations de jeux (difficulté, heures et note), critiques et votes « Il n'est plus obtenable ? ».",
 14: "<strong>Notifications :</strong> si tu les actives, un identifiant de notification Firebase Cloud Messaging pour que le serveur puisse t'envoyer des notifications.",
 16: "Ton ID en ligne, ton avatar, ton niveau, tes points et ton pays, ainsi que ce que tu publies, sont visibles par les autres utilisateurs dans les classements et dans la communauté.",
 24: "<strong>Sont supprimés :</strong> ton classement et ta progression, ta sauvegarde cloud, tes critiques, astuces, évaluations et heures de jeu, tes votes,\nles signalements que tu as faits, tes blocages et ton compte sur le serveur.",
 25: "<strong>Est conservé :</strong> uniquement le décompte anonyme des signalements visant le contenu des autres, sans qui a signalé, pour que ce qui a déjà été masqué le reste, tant que ce contenu existe.\nSi tu as écrit dans les groupes d'autres personnes dans d'anciennes versions de l'app, ces messages restent anonymes et sans texte.\nLes rapports de plantage de Crashlytics sont supprimés automatiquement au bout de 90 jours.",
 28: "Platinum Hunter ne s'adresse pas aux enfants de moins de 13 ans.",
 29: "Les fonctions communautaires (classement, sauvegarde cloud, astuces et critiques) enregistrent des données sur notre serveur. Si tu as moins de 14 ans (ou l'âge fixé par la loi de ton pays), tu as besoin de l'autorisation de ton père, de ta mère ou de ton tuteur pour les utiliser et pour accepter les annonces personnalisées, que tu peux refuser dans l'avis de consentement ou dans les réglages de l'app. Si nous apprenons qu'une personne n'ayant pas cet âge utilise la communauté sans cette autorisation, nous supprimons ses données du serveur.",
},
'de': {
 1: "Platinum Hunter zeigt die Trophäen deines PlayStation-Network-Kontos. Das meiste funktioniert nur auf deinem Gerät,\ndas mit den Servern von Sony kommuniziert. Die Community-Funktionen (Hunter-Level und Ranglisten, Tipps, Rezensionen, Bewertungen\nund die Cloud-Sicherung) nutzen unseren Server, gehostet bei Google Firebase (Google Cloud, Region Europäische Union, Belgien).\nSie werden nur aktiviert, wenn du dein Konto in der App bestätigst. Die App hat keinen eigenen Chat und keine eigenen Gruppen.",
 12: "<strong>Was du veröffentlichst:</strong> Tipps, Stimmen, Spielbewertungen (Schwierigkeit, Stunden und Note), Rezensionen und Stimmen zu „Nicht mehr erhältlich?“.",
 14: "<strong>Benachrichtigungen:</strong> wenn du sie aktivierst, eine Benachrichtigungs-ID von Firebase Cloud Messaging, damit der Server dir Benachrichtigungen schicken kann.",
 16: "Deine Online-ID, dein Avatar, Level, deine Punkte und dein Land sowie das, was du veröffentlichst, sind für andere Nutzer in den Ranglisten und in der Community sichtbar.",
 24: "<strong>Gelöscht werden:</strong> dein Ranking und dein Fortschritt, deine Cloud-Sicherung, deine Rezensionen, Tipps, Bewertungen und Spielstunden, deine Stimmen,\ndeine Meldungen, deine Blockierungen und dein Serverkonto.",
 25: "<strong>Erhalten bleibt:</strong> nur die anonyme Zahl der Meldungen zu Inhalten anderer, ohne wer gemeldet hat, damit bereits Ausgeblendetes ausgeblendet bleibt, solange dieser Inhalt existiert.\nWenn du in alten Versionen der App in Gruppen anderer geschrieben hast, bleiben diese Nachrichten anonym und ohne Text.\nAbsturzberichte von Crashlytics werden nach 90 Tagen automatisch gelöscht.",
 28: "Platinum Hunter richtet sich nicht an Kinder unter 13 Jahren.",
 29: "Die Community-Funktionen (Ranking, Cloud-Sicherung, Tipps und Rezensionen) speichern Daten auf unserem Server. Wenn du unter 14 bist (oder unter dem Alter, das das Gesetz deines Landes festlegt), brauchst du die Erlaubnis deiner Eltern oder deines Vormunds, um sie zu nutzen und personalisierte Werbung zu akzeptieren, die du im Einwilligungshinweis oder in den Einstellungen der App ablehnen kannst. Wenn wir erfahren, dass jemand unter diesem Alter die Community ohne diese Erlaubnis nutzt, löschen wir seine Daten vom Server.",
},
'it': {
 1: "Platinum Hunter mostra i trofei del tuo account PlayStation Network. Quasi tutto funziona solo sul tuo dispositivo,\nche comunica con i server di Sony. Le funzioni della community (Livello Hunter e classifiche, consigli, recensioni, valutazioni\ne il backup nel cloud) usano il nostro server, ospitato su Google Firebase (Google Cloud, regione Unione europea, Belgio).\nSi attivano solo se verifichi il tuo account nell'app. L'app non ha chat né gruppi propri.",
 12: "<strong>Ciò che pubblichi:</strong> consigli, voti, valutazioni dei giochi (difficoltà, ore e voto), recensioni e voti su «Non si può più ottenere?».",
 14: "<strong>Notifiche:</strong> se le attivi, un identificativo di notifica di Firebase Cloud Messaging perché il server possa inviarti notifiche.",
 16: "Il tuo ID online, avatar, livello, punti e paese, e ciò che pubblichi, sono visibili agli altri utenti nelle classifiche e nella community.",
 24: "<strong>Vengono eliminati:</strong> la tua classifica e i tuoi progressi, il backup nel cloud, le tue recensioni, consigli, valutazioni e ore di gioco, i tuoi voti,\nle segnalazioni che hai fatto, i tuoi blocchi e il tuo account sul server.",
 25: "<strong>Si conserva:</strong> solo il conteggio anonimo delle segnalazioni sui contenuti degli altri, senza chi ha segnalato, perché ciò che è già stato nascosto resti nascosto, finché quel contenuto esiste.\nSe hai scritto nei gruppi di altri nelle vecchie versioni dell'app, quei messaggi restano anonimi e senza testo.\nI rapporti sugli arresti anomali di Crashlytics si cancellano da soli dopo 90 giorni.",
 28: "Platinum Hunter non è rivolta ai minori di 13 anni.",
 29: "Le funzioni della community (classifica, backup nel cloud, consigli e recensioni) salvano dati sul nostro server. Se hai meno di 14 anni (o l'età stabilita dalla legge del tuo paese), ti serve il permesso di un genitore o tutore per usarle e per accettare gli annunci personalizzati, che puoi rifiutare nell'avviso di consenso o nelle impostazioni dell'app. Se veniamo a sapere che qualcuno sotto quell'età usa la community senza quel permesso, eliminiamo i suoi dati dal server.",
},
'pt-PT': {
 1: "O Platinum Hunter mostra os troféus da tua conta PlayStation Network. Quase tudo funciona só no teu dispositivo,\nque comunica com os servidores da Sony. As funções da comunidade (Nível Hunter e rankings, dicas, análises, avaliações\ne a cópia na nuvem) usam o nosso servidor, alojado no Google Firebase (Google Cloud, região da União Europeia, Bélgica).\nSó são ativadas se verificares a tua conta na app. A app não tem chat nem grupos próprios.",
 12: "<strong>O que publicas:</strong> dicas, votos, avaliações de jogos (dificuldade, horas e nota), análises e votos de «Não dá mais para conseguir».",
 14: "<strong>Notificações:</strong> se as ativares, um identificador de notificações do Firebase Cloud Messaging para que o servidor te possa enviar notificações.",
 16: "O teu ID online, avatar, nível, pontos e país, e o que publicas, são visíveis para outros utilizadores nos rankings e na comunidade.",
 24: "<strong>São apagados:</strong> o teu ranking e o teu progresso, a tua cópia na nuvem, as tuas análises, dicas, avaliações e horas de jogo, os teus votos,\nas denúncias que fizeste, os teus bloqueios e a tua conta do servidor.",
 25: "<strong>Conserva-se:</strong> só a contagem anónima de denúncias ao conteúdo de outros, sem quem denunciou, para que o que já foi ocultado continue oculto, enquanto esse conteúdo existir.\nSe escreveste em grupos de outros em versões antigas da app, essas mensagens ficam anónimas e sem texto.\nOs relatórios de falhas do Crashlytics apagam-se sozinhos ao fim de 90 dias.",
 28: "O Platinum Hunter não se destina a menores de 13 anos.",
 29: "As funções da comunidade (ranking, cópia na nuvem, dicas e análises) guardam dados no nosso servidor. Se tens menos de 14 anos (ou a idade que a lei do teu país fixar), precisas da autorização do teu pai, mãe ou tutor para as usar e para aceitar anúncios personalizados, que podes recusar no aviso de consentimento ou nas definições da app. Se soubermos que alguém abaixo dessa idade usa a comunidade sem essa autorização, apagamos os seus dados do servidor.",
},
'pt-BR': {
 1: "O Platinum Hunter mostra os troféus da sua conta PlayStation Network. Quase tudo funciona só no seu dispositivo,\nque se comunica com os servidores da Sony. Os recursos da comunidade (Nível Hunter e rankings, dicas, análises, avaliações\ne o backup na nuvem) usam nosso servidor, hospedado no Google Firebase (Google Cloud, região da União Europeia, Bélgica).\nEles só são ativados se você verificar sua conta no app. O app não tem chat nem grupos próprios.",
 12: "<strong>O que você publica:</strong> dicas, votos, avaliações de jogos (dificuldade, horas e nota), análises e votos de «Não dá mais para conseguir».",
 14: "<strong>Notificações:</strong> se você as ativar, um identificador de notificações do Firebase Cloud Messaging para que o servidor possa te enviar notificações.",
 16: "Seu ID online, avatar, nível, pontos e país, e o que você publica, ficam visíveis para outros usuários nos rankings e na comunidade.",
 24: "<strong>São apagados:</strong> seu ranking e seu progresso, seu backup na nuvem, suas análises, dicas, avaliações e horas de jogo, seus votos,\nas denúncias que você fez, seus bloqueios e sua conta do servidor.",
 25: "<strong>Fica guardada:</strong> só a contagem anônima de denúncias do conteúdo de outras pessoas, sem quem denunciou, para que o que já foi ocultado continue oculto, enquanto esse conteúdo existir.\nSe você escreveu em grupos de outras pessoas em versões antigas do app, essas mensagens ficam anônimas e sem texto.\nOs relatórios de falhas do Crashlytics são apagados automaticamente após 90 dias.",
 28: "O Platinum Hunter não é destinado a menores de 13 anos.",
 29: "Os recursos da comunidade (ranking, backup na nuvem, dicas e análises) guardam dados no nosso servidor. Se você tem menos de 14 anos (ou a idade definida pela lei do seu país), precisa da permissão do seu pai, mãe ou responsável para usá-los e para aceitar anúncios personalizados, que você pode recusar no aviso de consentimento ou nas configurações do app. Se soubermos que alguém abaixo dessa idade usa a comunidade sem essa permissão, apagamos os dados dessa pessoa do servidor.",
},
'nl': {
 1: "Platinum Hunter toont de trofeeën van je PlayStation Network-account. Het meeste werkt alleen op je apparaat,\ndat met de servers van Sony communiceert. De communityfuncties (Hunter-niveau en ranglijsten, tips, reviews, beoordelingen\nen de cloudback-up) gebruiken onze server, gehost bij Google Firebase (Google Cloud, regio Europese Unie, België).\nZe worden alleen ingeschakeld als je je account in de app verifieert. De app heeft geen eigen chat of groepen.",
 12: "<strong>Wat je publiceert:</strong> tips, stemmen, beoordelingen van games (moeilijkheid, uren en cijfer), reviews en stemmen bij ‘Niet meer te halen’.",
 14: "<strong>Meldingen:</strong> als je ze inschakelt, een meldings-ID van Firebase Cloud Messaging zodat de server je meldingen kan sturen.",
 16: "Je online-ID, avatar, niveau, punten en land, en wat je publiceert, zijn zichtbaar voor andere gebruikers in de ranglijsten en in de community.",
 24: "<strong>Verwijderd worden:</strong> je ranking en voortgang, je cloudback-up, je reviews, tips, beoordelingen en speeluren, je stemmen,\nde meldingen die je hebt gedaan, je blokkeringen en je serveraccount.",
 25: "<strong>Bewaard blijft:</strong> alleen het anonieme aantal meldingen over content van anderen, zonder wie meldde, zodat wat al verborgen is verborgen blijft, zolang die content bestaat.\nAls je in oude versies van de app in groepen van anderen hebt geschreven, blijven die berichten anoniem en zonder tekst.\nCrashrapporten van Crashlytics worden na 90 dagen automatisch verwijderd.",
 28: "Platinum Hunter is niet bedoeld voor kinderen jonger dan 13 jaar.",
 29: "De communityfuncties (ranking, cloudback-up, tips en reviews) slaan gegevens op onze server op. Als je jonger bent dan 14 (of de leeftijd die de wet van je land bepaalt), heb je toestemming nodig van je ouder of voogd om ze te gebruiken en om gepersonaliseerde advertenties te accepteren, die je kunt weigeren in de toestemmingsmelding of in de instellingen van de app. Als we merken dat iemand onder die leeftijd de community zonder die toestemming gebruikt, verwijderen we zijn gegevens van de server.",
},
'pl': {
 1: "Platinum Hunter pokazuje trofea z Twojego konta PlayStation Network. Większość działa tylko na Twoim urządzeniu,\nktóre łączy się z serwerami Sony. Funkcje społeczności (Poziom Hunter i rankingi, porady, recenzje, oceny\ni kopia w chmurze) korzystają z naszego serwera, hostowanego w Google Firebase (Google Cloud, region Unii Europejskiej, Belgia).\nWłączają się tylko wtedy, gdy zweryfikujesz konto w aplikacji. Aplikacja nie ma własnego czatu ani grup.",
 12: "<strong>To, co publikujesz:</strong> porady, głosy, oceny gier (trudność, godziny i ocena), recenzje oraz głosy „Nie da się go już zdobyć”.",
 14: "<strong>Powiadomienia:</strong> jeśli je włączysz, identyfikator powiadomień Firebase Cloud Messaging, aby serwer mógł wysyłać Ci powiadomienia.",
 16: "Twój identyfikator online, awatar, poziom, punkty i kraj oraz to, co publikujesz, są widoczne dla innych użytkowników w rankingach i w społeczności.",
 24: "<strong>Usuwane są:</strong> Twój ranking i postępy, kopia w chmurze, recenzje, porady, oceny i godziny gry, Twoje głosy,\nzgłoszenia, które wysłałeś, Twoje blokady i Twoje konto na serwerze.",
 25: "<strong>Zostaje:</strong> tylko anonimowa liczba zgłoszeń dotyczących treści innych osób, bez informacji, kto zgłosił, aby to, co już ukryto, pozostało ukryte, dopóki ta treść istnieje.\nJeśli w starych wersjach aplikacji pisałeś w grupach innych osób, te wiadomości pozostają anonimowe i bez treści.\nRaporty awarii Crashlytics usuwają się automatycznie po 90 dniach.",
 28: "Platinum Hunter nie jest przeznaczona dla dzieci poniżej 13 lat.",
 29: "Funkcje społeczności (ranking, kopia w chmurze, porady i recenzje) zapisują dane na naszym serwerze. Jeśli masz mniej niż 14 lat (lub mniej niż wiek ustalony przez prawo Twojego kraju), potrzebujesz zgody rodzica lub opiekuna, aby z nich korzystać i akceptować spersonalizowane reklamy, które możesz odrzucić w komunikacie o zgodzie lub w ustawieniach aplikacji. Jeśli dowiemy się, że ktoś poniżej tego wieku korzysta ze społeczności bez takiej zgody, usuniemy jego dane z serwera.",
},
'ru': {
 1: "Platinum Hunter показывает трофеи твоего аккаунта PlayStation Network. Почти всё работает только на твоём устройстве,\nкоторое связывается с серверами Sony. Функции сообщества (уровень Hunter и рейтинги, советы, отзывы, оценки\nи облачная копия) используют наш сервер, размещённый в Google Firebase (Google Cloud, регион Европейского союза, Бельгия).\nОни включаются, только если ты подтвердишь аккаунт в приложении. В приложении нет собственного чата и групп.",
 12: "<strong>То, что ты публикуешь:</strong> советы, голоса, оценки игр (сложность, часы и оценка), отзывы и голоса «Больше нельзя получить?».",
 14: "<strong>Уведомления:</strong> если ты их включишь, идентификатор уведомлений Firebase Cloud Messaging, чтобы сервер мог отправлять тебе уведомления.",
 16: "Твой онлайн-ID, аватар, уровень, очки и страна, а также то, что ты публикуешь, видны другим пользователям в рейтингах и в сообществе.",
 24: "<strong>Удаляются:</strong> твой рейтинг и прогресс, облачная копия, твои отзывы, советы, оценки и часы игры, твои голоса,\nжалобы, которые ты отправил, твои блокировки и твой аккаунт на сервере.",
 25: "<strong>Сохраняется:</strong> только анонимное число жалоб на контент других, без того, кто пожаловался, чтобы уже скрытое оставалось скрытым, пока этот контент существует.\nЕсли в старых версиях приложения ты писал в чужих группах, эти сообщения остаются анонимными и без текста.\nОтчёты о сбоях Crashlytics удаляются автоматически через 90 дней.",
 28: "Platinum Hunter не предназначено для детей младше 13 лет.",
 29: "Функции сообщества (рейтинг, облачная копия, советы и отзывы) хранят данные на нашем сервере. Если тебе меньше 14 лет (или возраста, установленного законом твоей страны), тебе нужно разрешение родителя или опекуна, чтобы пользоваться ими и соглашаться на персонализированную рекламу, от которой можно отказаться в окне согласия или в настройках приложения. Если мы узнаем, что кто-то младше этого возраста пользуется сообществом без такого разрешения, мы удалим его данные с сервера.",
},
'uk': {
 1: "Platinum Hunter показує трофеї твого акаунта PlayStation Network. Майже все працює лише на твоєму пристрої,\nякий зв'язується із серверами Sony. Функції спільноти (рівень Hunter і рейтинги, поради, відгуки, оцінки\nта хмарна копія) використовують наш сервер, розміщений у Google Firebase (Google Cloud, регіон Європейського Союзу, Бельгія).\nВони вмикаються, лише якщо ти підтвердиш акаунт у застосунку. У застосунку немає власного чату й груп.",
 12: "<strong>Те, що ти публікуєш:</strong> поради, голоси, оцінки ігор (складність, години й оцінка), відгуки та голоси «Більше не можна отримати?».",
 14: "<strong>Сповіщення:</strong> якщо ти їх увімкнеш, ідентифікатор сповіщень Firebase Cloud Messaging, щоб сервер міг надсилати тобі сповіщення.",
 16: "Твій онлайн-ID, аватар, рівень, очки й країна, а також те, що ти публікуєш, видно іншим користувачам у рейтингах і в спільноті.",
 24: "<strong>Видаляються:</strong> твій рейтинг і прогрес, хмарна копія, твої відгуки, поради, оцінки й години гри, твої голоси,\nскарги, які ти надіслав, твої блокування та твій акаунт на сервері.",
 25: "<strong>Зберігається:</strong> лише анонімна кількість скарг на вміст інших, без того, хто поскаржився, щоб уже приховане лишалося прихованим, доки цей вміст існує.\nЯкщо в старих версіях застосунку ти писав у чужих групах, ці повідомлення лишаються анонімними й без тексту.\nЗвіти про збої Crashlytics видаляються автоматично через 90 днів.",
 28: "Platinum Hunter не призначений для дітей молодше 13 років.",
 29: "Функції спільноти (рейтинг, хмарна копія, поради й відгуки) зберігають дані на нашому сервері. Якщо тобі менше 14 років (або віку, встановленого законом твоєї країни), потрібен дозвіл батьків чи опікуна, щоб користуватися ними й погоджуватися на персоналізовану рекламу, від якої можна відмовитися у вікні згоди або в налаштуваннях застосунку. Якщо ми дізнаємося, що хтось молодший за цей вік користується спільнотою без такого дозволу, ми видалимо його дані із сервера.",
},
'tr': {
 1: "Platinum Hunter, PlayStation Network hesabının kupalarını gösterir. Çoğu yalnızca Sony sunucularıyla iletişim kuran\ncihazında çalışır. Topluluk özellikleri (Hunter Seviyesi ve sıralamalar, ipuçları, incelemeler, değerlendirmeler\nve bulut yedeği) Google Firebase'de (Google Cloud, Avrupa Birliği bölgesi, Belçika) barındırılan sunucumuzu kullanır.\nYalnızca uygulamada hesabını doğrularsan açılır. Uygulamanın kendine ait sohbeti veya grupları yoktur.",
 12: "<strong>Paylaştıkların:</strong> ipuçları, oylar, oyun değerlendirmeleri (zorluk, süre ve puan), incelemeler ve “Artık alınamıyor mu?” oyları.",
 14: "<strong>Bildirimler:</strong> açarsan, sunucunun sana bildirim gönderebilmesi için bir Firebase Cloud Messaging bildirim kimliği.",
 16: "Çevrimiçi kimliğin, avatarın, seviyen, puanların, ülken ve paylaştıkların sıralamalarda ve toplulukta diğer kullanıcılar tarafından görülebilir.",
 24: "<strong>Silinenler:</strong> sıralaman ve ilerlemen, bulut yedeğin, incelemelerin, ipuçların, değerlendirmelerin ve oyun sürelerin, oyların,\nyaptığın şikâyetler, engellemelerin ve sunucudaki hesabın.",
 25: "<strong>Saklanan:</strong> yalnızca başkalarının içeriğine yapılan şikâyetlerin, kimin şikâyet ettiği olmadan anonim sayısı; böylece gizlenmiş olan gizli kalır. O içerik var olduğu sürece saklanır.\nUygulamanın eski sürümlerinde başkalarının gruplarına yazdıysan, o mesajlar anonim ve metinsiz kalır.\nCrashlytics çökme raporları 90 gün sonra kendiliğinden silinir.",
 28: "Platinum Hunter 13 yaşından küçük çocuklara yönelik değildir.",
 29: "Topluluk özellikleri (sıralama, bulut yedeği, ipuçları ve incelemeler) sunucumuzda veri saklar. 14 yaşından küçüksen (veya ülkenin yasasının belirlediği yaştan küçüksen), bunları kullanmak ve kişiselleştirilmiş reklamları kabul etmek için annenin, babanın veya vasinin iznine ihtiyacın var; bu reklamları onay bildiriminde veya uygulama ayarlarında reddedebilirsin. Bu yaşın altındaki birinin bu izin olmadan topluluğu kullandığını öğrenirsek, verilerini sunucudan sileriz.",
},
'ja': {
 1: "Platinum Hunterは、あなたのPlayStation Networkアカウントのトロフィーを表示します。ほとんどの機能はSonyのサーバーと通信するあなたの端末だけで動作します。\nコミュニティ機能（Hunterレベルとランキング、ヒント、レビュー、評価、クラウドバックアップ）は、Google Firebase（Google Cloud、欧州連合リージョン、ベルギー）にある当社のサーバーを使います。\nアプリでアカウントを認証した場合にのみ有効になります。アプリ独自のチャットやグループはありません。",
 12: "<strong>あなたが投稿するもの：</strong>ヒント、投票、ゲームの評価（難易度、時間、スコア）、レビュー、「もう取得できない」への投票。",
 14: "<strong>通知：</strong>オンにした場合、サーバーから通知を送るためのFirebase Cloud Messagingの通知ID。",
 16: "あなたのオンラインID、アバター、レベル、ポイント、国、そして投稿した内容は、ランキングとコミュニティで他のユーザーに表示されます。",
 24: "<strong>削除されるもの：</strong>ランキングと進行状況、クラウドバックアップ、レビュー、ヒント、評価とプレイ時間、投票、\nあなたが行った通報、ブロック、サーバーのアカウント。",
 25: "<strong>残るもの：</strong>他の人のコンテンツへの通報の匿名の件数だけです（誰が通報したかは残りません）。すでに非表示になったものを非表示のままにするためで、そのコンテンツが存在する間だけ保管します。\n古いバージョンのアプリで他の人のグループに書き込んだ場合、そのメッセージは匿名で本文のない状態になります。\nCrashlyticsのクラッシュレポートは90日後に自動で削除されます。",
 28: "Platinum Hunterは13歳未満のお子様を対象としていません。",
 29: "コミュニティ機能（ランキング、クラウドバックアップ、ヒント、レビュー）は当社のサーバーにデータを保存します。14歳未満（またはお住まいの国の法律で定める年齢未満）の方は、これらを利用したりパーソナライズド広告に同意したりするには保護者の許可が必要です。広告は同意画面またはアプリの設定で拒否できます。その年齢未満の方が許可なくコミュニティを利用していると分かった場合、サーバーからそのデータを削除します。",
},
'ko': {
 1: "Platinum Hunter는 PlayStation Network 계정의 트로피를 보여 줍니다. 대부분의 기능은 Sony 서버와 통신하는 사용자의 기기에서만 작동합니다.\n커뮤니티 기능(Hunter 레벨과 랭킹, 팁, 리뷰, 평가, 클라우드 백업)은 Google Firebase(Google Cloud, 유럽연합 리전, 벨기에)에 있는 당사 서버를 사용합니다.\n앱에서 계정을 인증한 경우에만 켜집니다. 앱에는 자체 채팅이나 그룹이 없습니다.",
 12: "<strong>사용자가 게시하는 콘텐츠:</strong> 팁, 투표, 게임 평가(난이도, 소요 시간, 점수), 리뷰, ‘더 이상 획득 불가’ 투표.",
 14: "<strong>알림:</strong> 알림을 켜면, 서버가 알림을 보낼 수 있도록 Firebase Cloud Messaging 알림 ID.",
 16: "온라인 ID, 아바타, 레벨, 포인트, 국가와 게시한 콘텐츠는 랭킹과 커뮤니티에서 다른 사용자에게 표시됩니다.",
 24: "<strong>삭제되는 항목:</strong> 랭킹과 진행 상황, 클라우드 백업, 리뷰, 팁, 평가와 플레이 시간, 투표,\n내가 한 신고, 차단 목록, 서버 계정.",
 25: "<strong>남는 항목:</strong> 다른 사람의 콘텐츠에 대한 신고의 익명 건수만 남으며, 누가 신고했는지는 남지 않습니다. 이미 숨겨진 콘텐츠가 계속 숨겨지도록 하기 위한 것이며, 해당 콘텐츠가 있는 동안만 보관합니다.\n이전 버전의 앱에서 다른 사람의 그룹에 글을 썼다면, 그 메시지는 익명이 되고 내용이 지워집니다.\nCrashlytics 오류 보고서는 90일 후 자동으로 삭제됩니다.",
 28: "Platinum Hunter는 13세 미만 아동을 대상으로 하지 않습니다.",
 29: "커뮤니티 기능(랭킹, 클라우드 백업, 팁, 리뷰)은 당사 서버에 데이터를 저장합니다. 14세 미만(또는 거주 국가의 법률이 정한 연령 미만)이라면, 이 기능을 사용하고 맞춤 광고에 동의하려면 부모님이나 보호자의 허락이 필요합니다. 맞춤 광고는 동의 안내나 앱 설정에서 거부할 수 있습니다. 해당 연령 미만인 사람이 허락 없이 커뮤니티를 사용하는 것을 알게 되면, 서버에서 그 데이터를 삭제합니다.",
},
'zh-Hans': {
 1: "Platinum Hunter 显示你的 PlayStation Network 账号的奖杯。大部分功能只在你的设备上运行，由设备直接与 Sony 的服务器通信。\n社区功能（Hunter 等级和排行榜、技巧、评论、评分以及云端备份）使用我们托管在 Google Firebase（Google Cloud，欧盟区域，比利时）上的服务器。\n只有在你于应用中验证账号后才会启用。应用没有自己的聊天或群组功能。",
 12: "<strong>你发布的内容：</strong>技巧、投票、游戏评分（难度、时长和分数）、评论以及“已无法获得”投票。",
 14: "<strong>通知：</strong>如果你开启通知，会保存一个 Firebase Cloud Messaging 通知标识符，以便服务器向你发送通知。",
 16: "你的在线 ID、头像、等级、积分和国家/地区，以及你发布的内容，会在排行榜和社区中对其他用户可见。",
 24: "<strong>会删除：</strong>你的排名和进度、云端备份、你的评论、技巧、评分和游戏时长、你的投票、\n你提交的举报、你的屏蔽列表以及你在服务器上的账号。",
 25: "<strong>会保留：</strong>只保留针对他人内容的举报的匿名计数，不含举报者，以便已隐藏的内容保持隐藏；只要该内容存在就会保留。\n如果你在旧版应用中于他人的群组发过消息，这些消息会变为匿名且不含正文。\nCrashlytics 崩溃报告会在 90 天后自动删除。",
 28: "Platinum Hunter 不面向 13 岁以下的儿童。",
 29: "社区功能（排行榜、云端备份、技巧和评论）会在我们的服务器上保存数据。如果你未满 14 岁（或你所在国家法律规定的年龄），使用这些功能以及接受个性化广告都需要得到父母或监护人的许可；你可以在同意提示或应用设置中拒绝个性化广告。如果我们得知未满该年龄的人在未获许可的情况下使用社区，我们会从服务器删除其数据。",
},
'zh-Hant': {
 1: "Platinum Hunter 顯示你的 PlayStation Network 帳號的獎盃。大部分功能只在你的裝置上執行，由裝置直接與 Sony 的伺服器通訊。\n社群功能（Hunter 等級和排行榜、技巧、評論、評分以及雲端備份）使用我們託管在 Google Firebase（Google Cloud，歐盟區域，比利時）上的伺服器。\n只有在你於應用程式中驗證帳號後才會啟用。應用程式沒有自己的聊天或群組功能。",
 12: "<strong>你發布的內容：</strong>技巧、投票、遊戲評分（難度、時數和分數）、評論以及「已無法獲得」投票。",
 14: "<strong>通知：</strong>如果你開啟通知，會保存一個 Firebase Cloud Messaging 通知識別碼，讓伺服器可以傳送通知給你。",
 16: "你的線上 ID、頭像、等級、積分和國家/地區，以及你發布的內容，會在排行榜和社群中對其他使用者顯示。",
 24: "<strong>會刪除：</strong>你的排名和進度、雲端備份、你的評論、技巧、評分和遊戲時數、你的投票、\n你提出的檢舉、你的封鎖清單以及你在伺服器上的帳號。",
 25: "<strong>會保留：</strong>只保留針對他人內容的檢舉的匿名計數，不含檢舉者，讓已隱藏的內容維持隱藏；只要該內容存在就會保留。\n如果你在舊版應用程式中於他人的群組傳過訊息，這些訊息會變為匿名且不含內文。\nCrashlytics 當機報告會在 90 天後自動刪除。",
 28: "Platinum Hunter 不以未滿 13 歲的兒童為對象。",
 29: "社群功能（排行榜、雲端備份、技巧和評論）會在我們的伺服器上保存資料。如果你未滿 14 歲（或你所在國家法律規定的年齡），使用這些功能以及接受個人化廣告都需要父母或監護人的許可；你可以在同意提示或應用程式設定中拒絕個人化廣告。如果我們得知未滿該年齡的人在未經許可的情況下使用社群，我們會從伺服器刪除其資料。",
},
'ar': {
 1: "يعرض Platinum Hunter كؤوس حسابك على PlayStation Network. يعمل معظمه على جهازك فقط،\nالذي يتواصل مع خوادم Sony. تستخدم ميزات المجتمع (مستوى Hunter والتصنيفات والنصائح والمراجعات والتقييمات\nوالنسخة الاحتياطية السحابية) خادمنا المستضاف على Google Firebase (Google Cloud، منطقة الاتحاد الأوروبي، بلجيكا).\nولا تعمل إلا إذا تحققت من حسابك في التطبيق. لا يحتوي التطبيق على دردشة أو مجموعات خاصة به.",
 12: "<strong>ما تنشره:</strong> النصائح، والأصوات، وتقييمات الألعاب (الصعوبة والساعات والدرجة)، والمراجعات، وأصوات «لم يعد بالإمكان الحصول عليها».",
 14: "<strong>الإشعارات:</strong> إذا فعّلتها، معرّف إشعارات من Firebase Cloud Messaging حتى يتمكن الخادم من إرسال الإشعارات إليك.",
 16: "معرّفك على الإنترنت وصورتك الرمزية ومستواك ونقاطك وبلدك، وما تنشره، مرئية للمستخدمين الآخرين في التصنيفات وفي المجتمع.",
 24: "<strong>يُحذف:</strong> تصنيفك وتقدمك، ونسختك الاحتياطية السحابية، ومراجعاتك ونصائحك وتقييماتك وساعات لعبك، وأصواتك،\nوالبلاغات التي قدّمتها، وقائمة الحظر لديك، وحسابك على الخادم.",
 25: "<strong>يُحتفظ فقط:</strong> بالعدد المجهول الهوية للبلاغات عن محتوى الآخرين، دون معرفة من أبلغ، حتى يبقى ما أُخفي مخفيًا، وذلك طالما بقي ذلك المحتوى موجودًا.\nإذا كتبت في مجموعات الآخرين في إصدارات قديمة من التطبيق، تبقى تلك الرسائل مجهولة الهوية وبلا نص.\nتُحذف تقارير الأعطال من Crashlytics تلقائيًا بعد 90 يومًا.",
 28: "Platinum Hunter غير موجّه للأطفال دون 13 عامًا.",
 29: "تحفظ ميزات المجتمع (التصنيف والنسخة الاحتياطية السحابية والنصائح والمراجعات) بيانات على خادمنا. إذا كان عمرك أقل من 14 عامًا (أو السن التي يحددها قانون بلدك)، فأنت بحاجة إلى إذن والدك أو والدتك أو الوصي عليك لاستخدامها ولقبول الإعلانات المخصصة، ويمكنك رفضها في إشعار الموافقة أو في إعدادات التطبيق. إذا علمنا أن شخصًا دون هذه السن يستخدم المجتمع دون هذا الإذن، نحذف بياناته من الخادم.",
},
'hi': {
 1: "Platinum Hunter आपके PlayStation Network खाते की ट्रॉफ़ियाँ दिखाता है। इसका ज़्यादातर हिस्सा सिर्फ़ आपके डिवाइस पर चलता है,\nजो Sony के सर्वर से बात करता है। कम्युनिटी सुविधाएँ (Hunter लेवल और रैंकिंग, टिप्स, रिव्यू, रेटिंग\nऔर क्लाउड बैकअप) हमारे सर्वर का इस्तेमाल करती हैं, जो Google Firebase (Google Cloud, यूरोपीय संघ क्षेत्र, बेल्जियम) पर होस्ट है।\nये तभी चालू होती हैं जब आप ऐप में अपना खाता सत्यापित करते हैं। ऐप में अपनी कोई चैट या समूह नहीं है।",
 12: "<strong>आप जो प्रकाशित करते हैं:</strong> टिप्स, वोट, गेम रेटिंग (कठिनाई, घंटे और स्कोर), रिव्यू और “अब नहीं मिल सकती” वाले वोट।",
 14: "<strong>सूचनाएँ:</strong> अगर आप इन्हें चालू करते हैं, तो Firebase Cloud Messaging का एक सूचना आईडी, ताकि सर्वर आपको सूचनाएँ भेज सके।",
 16: "आपकी ऑनलाइन आईडी, अवतार, लेवल, पॉइंट और देश, और आप जो प्रकाशित करते हैं, रैंकिंग और कम्युनिटी में दूसरे उपयोगकर्ताओं को दिखते हैं।",
 24: "<strong>हटाया जाता है:</strong> आपकी रैंकिंग और प्रगति, क्लाउड बैकअप, आपके रिव्यू, टिप्स, रेटिंग और खेलने के घंटे, आपके वोट,\nआपकी की गई शिकायतें, आपकी ब्लॉक सूची और सर्वर पर आपका खाता।",
 25: "<strong>रखा जाता है:</strong> सिर्फ़ दूसरों की सामग्री पर हुई शिकायतों की गुमनाम गिनती, बिना यह बताए कि शिकायत किसने की, ताकि जो पहले से छिपा है वह छिपा रहे; यह तब तक रहती है जब तक वह सामग्री मौजूद है।\nअगर आपने ऐप के पुराने संस्करणों में दूसरों के समूहों में लिखा था, तो वे संदेश गुमनाम और बिना टेक्स्ट के रहते हैं।\nCrashlytics की क्रैश रिपोर्ट 90 दिनों के बाद अपने आप हट जाती हैं।",
 28: "Platinum Hunter 13 साल से कम उम्र के बच्चों के लिए नहीं है।",
 29: "कम्युनिटी सुविधाएँ (रैंकिंग, क्लाउड बैकअप, टिप्स और रिव्यू) हमारे सर्वर पर डेटा रखती हैं। अगर आपकी उम्र 14 साल से कम है (या आपके देश के कानून में तय उम्र से कम), तो इन्हें इस्तेमाल करने और पर्सनलाइज़्ड विज्ञापन स्वीकार करने के लिए आपको अपने माता-पिता या अभिभावक की अनुमति चाहिए; इन विज्ञापनों को आप सहमति सूचना में या ऐप की सेटिंग में मना कर सकते हैं। अगर हमें पता चलता है कि उस उम्र से कम कोई व्यक्ति बिना अनुमति कम्युनिटी इस्तेमाल कर रहा है, तो हम उसका डेटा सर्वर से हटा देते हैं।",
},
'id': {
 1: "Platinum Hunter menampilkan trofi akun PlayStation Network-mu. Sebagian besar hanya berjalan di perangkatmu,\nyang berkomunikasi dengan server Sony. Fitur komunitas (Level Hunter dan peringkat, tips, ulasan, penilaian\nserta cadangan cloud) memakai server kami, yang di-hosting di Google Firebase (Google Cloud, wilayah Uni Eropa, Belgia).\nFitur ini hanya aktif jika kamu memverifikasi akunmu di aplikasi. Aplikasi ini tidak punya obrolan atau grup sendiri.",
 12: "<strong>Yang kamu publikasikan:</strong> tips, vote, penilaian game (kesulitan, jam, dan skor), ulasan, dan vote “Sudah tidak bisa didapat”.",
 14: "<strong>Notifikasi:</strong> jika kamu mengaktifkannya, ID notifikasi Firebase Cloud Messaging agar server bisa mengirimimu notifikasi.",
 16: "ID online, avatar, level, poin, dan negaramu, serta yang kamu publikasikan, terlihat oleh pengguna lain di peringkat dan di komunitas.",
 24: "<strong>Yang dihapus:</strong> peringkat dan progresmu, cadangan cloud, ulasan, tips, penilaian, dan jam bermainmu, vote-mu,\nlaporan yang kamu buat, daftar blokirmu, dan akunmu di server.",
 25: "<strong>Yang disimpan:</strong> hanya jumlah anonim laporan atas konten orang lain, tanpa siapa yang melapor, agar yang sudah disembunyikan tetap tersembunyi, selama konten itu masih ada.\nJika kamu pernah menulis di grup orang lain di versi lama aplikasi, pesan itu tetap anonim dan tanpa teks.\nLaporan error Crashlytics terhapus otomatis setelah 90 hari.",
 28: "Platinum Hunter tidak ditujukan untuk anak di bawah 13 tahun.",
 29: "Fitur komunitas (peringkat, cadangan cloud, tips, dan ulasan) menyimpan data di server kami. Jika usiamu di bawah 14 tahun (atau usia yang ditetapkan hukum di negaramu), kamu perlu izin dari orang tua atau wali untuk memakainya dan untuk menerima iklan yang dipersonalisasi, yang bisa kamu tolak di pemberitahuan persetujuan atau di pengaturan aplikasi. Jika kami tahu ada orang di bawah usia itu yang memakai komunitas tanpa izin tersebut, kami menghapus datanya dari server.",
},
'th': {
 1: "Platinum Hunter แสดงถ้วยรางวัลของบัญชี PlayStation Network ของคุณ ส่วนใหญ่ทำงานบนอุปกรณ์ของคุณเท่านั้น\nซึ่งติดต่อกับเซิร์ฟเวอร์ของ Sony ฟีเจอร์ชุมชน (เลเวล Hunter และอันดับ เคล็ดลับ รีวิว การให้คะแนน\nและข้อมูลสำรองบนคลาวด์) ใช้เซิร์ฟเวอร์ของเราที่โฮสต์บน Google Firebase (Google Cloud ภูมิภาคสหภาพยุโรป เบลเยียม)\nและจะเปิดใช้เฉพาะเมื่อคุณยืนยันบัญชีในแอปเท่านั้น แอปไม่มีแชทหรือกลุ่มของตัวเอง",
 12: "<strong>สิ่งที่คุณเผยแพร่:</strong> เคล็ดลับ โหวต การให้คะแนนเกม (ความยาก ชั่วโมง และคะแนน) รีวิว และโหวต “ไม่สามารถรับได้อีกแล้ว”",
 14: "<strong>การแจ้งเตือน:</strong> หากคุณเปิดใช้ จะมีรหัสการแจ้งเตือนของ Firebase Cloud Messaging เพื่อให้เซิร์ฟเวอร์ส่งการแจ้งเตือนถึงคุณได้",
 16: "ID ออนไลน์ อวาตาร์ เลเวล คะแนน และประเทศของคุณ รวมถึงสิ่งที่คุณเผยแพร่ จะแสดงให้ผู้ใช้อื่นเห็นในอันดับและในชุมชน",
 24: "<strong>สิ่งที่ถูกลบ:</strong> อันดับและความคืบหน้าของคุณ ข้อมูลสำรองบนคลาวด์ รีวิว เคล็ดลับ การให้คะแนนและชั่วโมงการเล่น โหวตของคุณ\nรายงานที่คุณส่ง รายชื่อที่คุณบล็อก และบัญชีของคุณบนเซิร์ฟเวอร์",
 25: "<strong>สิ่งที่เก็บไว้:</strong> มีเพียงจำนวนรายงานแบบไม่ระบุตัวตนต่อเนื้อหาของผู้อื่น โดยไม่ระบุผู้รายงาน เพื่อให้สิ่งที่ซ่อนไปแล้วยังคงถูกซ่อน และเก็บไว้ตราบเท่าที่เนื้อหานั้นยังอยู่\nหากคุณเคยเขียนในกลุ่มของผู้อื่นในแอปเวอร์ชันเก่า ข้อความเหล่านั้นจะเป็นแบบไม่ระบุตัวตนและไม่มีข้อความ\nรายงานข้อขัดข้องของ Crashlytics จะถูกลบโดยอัตโนมัติหลังจาก 90 วัน",
 28: "Platinum Hunter ไม่ได้มุ่งเป้าไปที่เด็กอายุต่ำกว่า 13 ปี",
 29: "ฟีเจอร์ชุมชน (อันดับ ข้อมูลสำรองบนคลาวด์ เคล็ดลับ และรีวิว) จะเก็บข้อมูลไว้บนเซิร์ฟเวอร์ของเรา หากคุณอายุต่ำกว่า 14 ปี (หรืออายุที่กฎหมายในประเทศของคุณกำหนด) คุณต้องได้รับอนุญาตจากพ่อแม่หรือผู้ปกครองก่อนใช้งานและก่อนยอมรับโฆษณาที่ปรับตามความสนใจ ซึ่งคุณปฏิเสธได้ในประกาศขอความยินยอมหรือในการตั้งค่าของแอป หากเราทราบว่ามีผู้ที่อายุต่ำกว่านั้นใช้ชุมชนโดยไม่ได้รับอนุญาต เราจะลบข้อมูลของผู้นั้นออกจากเซิร์ฟเวอร์",
},
'vi': {
 1: "Platinum Hunter hiển thị các chiếc cúp trong tài khoản PlayStation Network của bạn. Phần lớn chỉ chạy trên thiết bị của bạn,\nthiết bị giao tiếp với máy chủ của Sony. Các tính năng cộng đồng (Cấp độ Hunter và bảng xếp hạng, mẹo, bài nhận xét, đánh giá\nvà bản sao lưu đám mây) dùng máy chủ của chúng tôi, đặt tại Google Firebase (Google Cloud, khu vực Liên minh châu Âu, Bỉ).\nChúng chỉ được bật nếu bạn xác minh tài khoản trong ứng dụng. Ứng dụng không có tính năng trò chuyện hay nhóm riêng.",
 12: "<strong>Nội dung bạn đăng:</strong> mẹo, lượt bình chọn, đánh giá game (độ khó, số giờ và điểm), bài nhận xét và phiếu “Không còn lấy được”.",
 14: "<strong>Thông báo:</strong> nếu bạn bật, một mã thông báo Firebase Cloud Messaging để máy chủ có thể gửi thông báo cho bạn.",
 16: "ID trực tuyến, ảnh đại diện, cấp độ, điểm và quốc gia của bạn, cùng nội dung bạn đăng, được người dùng khác nhìn thấy trong bảng xếp hạng và trong cộng đồng.",
 24: "<strong>Bị xóa:</strong> thứ hạng và tiến trình, bản sao lưu đám mây, bài nhận xét, mẹo, đánh giá và số giờ chơi, lượt bình chọn,\ncác báo cáo bạn đã gửi, danh sách chặn và tài khoản của bạn trên máy chủ.",
 25: "<strong>Được giữ lại:</strong> chỉ số lượng báo cáo ẩn danh về nội dung của người khác, không ghi ai đã báo cáo, để nội dung đã bị ẩn vẫn bị ẩn, và chỉ trong thời gian nội dung đó còn tồn tại.\nNếu bạn từng viết trong nhóm của người khác ở các phiên bản cũ của ứng dụng, các tin nhắn đó vẫn ẩn danh và không còn nội dung.\nBáo cáo sự cố của Crashlytics tự động bị xóa sau 90 ngày.",
 28: "Platinum Hunter không dành cho trẻ em dưới 13 tuổi.",
 29: "Các tính năng cộng đồng (bảng xếp hạng, bản sao lưu đám mây, mẹo và bài nhận xét) lưu dữ liệu trên máy chủ của chúng tôi. Nếu bạn dưới 14 tuổi (hoặc độ tuổi do luật pháp nước bạn quy định), bạn cần sự cho phép của cha mẹ hoặc người giám hộ để sử dụng chúng và để chấp nhận quảng cáo được cá nhân hóa; bạn có thể từ chối quảng cáo này trong thông báo đồng ý hoặc trong phần cài đặt của ứng dụng. Nếu chúng tôi biết có người dưới độ tuổi đó dùng cộng đồng mà không có sự cho phép, chúng tôi sẽ xóa dữ liệu của họ khỏi máy chủ.",
},
}

PAT = re.compile(r'<(p|li)>(.*?)</\1>', re.S)

assert len(T) == 22, len(T)
for loc, blocks in T.items():
    f = os.path.join(TX, loc + '.json')
    d = json.load(open(f, encoding='utf-8'))
    p = d['privacy_html']
    ms = list(PAT.finditer(p))
    assert len(ms) == 32, (loc, len(ms))
    assert FB in ms[1].group(2) or 'Firebase' in ms[1].group(2), loc
    out, last = [], 0
    for i, m in enumerate(ms):
        if i in blocks:
            out.append(p[last:m.start(2)]); out.append(blocks[i]); last = m.end(2)
    out.append(p[last:])
    d['privacy_html'] = ''.join(out)
    d['privacy_updated'] = re.sub(r'(?<!\d)9(?!\d)', '14', d['privacy_updated'], count=1)
    with open(f, 'w', encoding='utf-8') as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2)
        fh.write('\n')
    print('ok', loc, d['privacy_updated'])
