from pydantic import BaseModel


class ResolvedRecipient(BaseModel):
    """
    Represents one successfully resolved
    Microsoft Entra user.
    """

    user_id: str
    display_name: str
    email: str


class RecipientSearchResult(BaseModel):
    """
    Output returned by the resolver.

    status

        resolved
        multiple_matches
        not_found
    """

    status: str

    recipient: ResolvedRecipient | None = None

    matches: list[ResolvedRecipient] = []